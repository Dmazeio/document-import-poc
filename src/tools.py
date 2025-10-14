import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Set, Literal
import json

# --- MODIFIED MODELS ---
class BatchMatchResult(BaseModel):
    input_text: str = Field(..., description="The original text snippet that was being matched.")
    entity_type: str = Field(..., description="The entity type for this snippet (e.g., 'people', 'project').")
    best_match_id: Optional[str] = Field(..., description="The ID of the best matching entity. Null if no confident match was found.")
    confidence: Literal["High", "Medium", "Low"] = Field(..., description="Your confidence in this match. 'High' for an exact match, 'Medium' for a likely partial match, 'Low' for a guess.")
    reasoning: str = Field(..., description="A brief explanation for the choice, justifying the confidence level.")

class BatchMatchResponse(BaseModel):
    matches: List[BatchMatchResult]

# --- MODIFIED BATCH FUNCTION ---
def find_best_entity_matches_in_batch(
    client: OpenAI,
    items_to_match: Dict[str, Set[str]],
    valid_entities_map: Dict[str, List[Dict]]
) -> Dict[str, Dict[str, dict]]:
    """
    Finds the best ID matches for a batch of text snippets across different entity types in a single AI call.
    Returns a richer dictionary containing the ID, confidence, and reasoning for each match.
    """
    if not items_to_match:
        return {}

    instructor_client = instructor.patch(client)

    tasks_list = []
    for entity_type, texts in items_to_match.items():
        for text in texts:
            tasks_list.append({"text": text, "entity_type": entity_type})

    system_prompt = """
    You are an expert in high-throughput entity resolution. Your task is to process a batch of text snippets and find the single best matching entity for each from a provided database of valid entities.
    The provided lists of entities are the ONLY source of truth.

    For each snippet, you MUST return the following:
    1. `input_text`: The original text.
    2. `entity_type`: The original entity type.
    3. `best_match_id`: The ID of the best match. Null if no confident match is found.
    4. `confidence`: Your confidence level for the match: "High", "Medium", or "Low".
    5. `reasoning`: A concise explanation for your choice. This reasoning MUST justify the confidence level (e.g., "Exact match", "Partial match on last name", "Ambiguous, best guess").

    For entity types that represent predefined lists of options (e.g., statuses like 'measurestate', priorities, types), where the input text might be a descriptive phrase, find the most semantically appropriate match from the provided valid options. An exact text match is not always required for these types; prioritize the meaning and choose the closest available option.

    If no good match is found for a snippet, you MUST return null for `best_match_id` and "Low" for `confidence`.
    """

    user_prompt = f"""
    Here is the database of all available entities, categorized by type:
    --- DATABASE OF ENTITIES ---
    {json.dumps(valid_entities_map, indent=2, ensure_ascii=False)}
    --- END OF DATABASE ---

    Now, please process the following list of matching tasks:
    --- TASKS TO PROCESS ---
    {json.dumps(tasks_list, indent=2, ensure_ascii=False)}
    --- END OF TASKS ---

    Return a complete list of results for all tasks.
    """

    try:
        response = instructor_client.chat.completions.create(
            model="gpt-4o",
            response_model=BatchMatchResponse,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_retries=1
        )

        detailed_lookup_map = {}
        for match in response.matches:
            if match.best_match_id:
                if match.entity_type not in detailed_lookup_map:
                    detailed_lookup_map[match.entity_type] = {}
                
                detailed_lookup_map[match.entity_type][match.input_text] = {
                    "id": match.best_match_id,
                    "confidence": match.confidence,
                    "reasoning": match.reasoning
                }
                print(f"  - [BATCH MATCHER] Matched '{match.input_text}' ({match.entity_type}) -> ID: {match.best_match_id} (Confidence: {match.confidence})")
            else:
                print(f"  - [BATCH MATCHER] Match NOT FOUND for '{match.input_text}' ({match.entity_type}). Reasoning: {match.reasoning} (Confidence: {match.confidence})")

        return detailed_lookup_map
            
    except Exception as e:
        print(f"  - [BATCH MATCHER] CRITICAL ERROR during batch entity matching: {e}")
        return {}