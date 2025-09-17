# File: src/tools.py (NEW BATCH-PROCESSING VERSION)

import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Set
import json
# --- NYE MODELLER FOR BATCH-PROSESSERING ---
class BatchMatchResult(BaseModel):
    input_text: str = Field(..., description="The original text snippet that was being matched.")
    entity_type: str = Field(..., description="The entity type for this snippet (e.g., 'people', 'project').")
    best_match_id: Optional[str] = Field(..., description="The ID of the best matching entity. Null if no confident match was found.")
    reasoning: str = Field(..., description="A brief explanation for the choice.")

class BatchMatchResponse(BaseModel):
    matches: List[BatchMatchResult]

# --- NY OG FORBEDRET BATCH-FUNKSJON ---
def find_best_entity_matches_in_batch(
    client: OpenAI,
    items_to_match: Dict[str, Set[str]],
    valid_entities_map: Dict[str, List[Dict]]
) -> Dict[str, Dict[str, str]]:
    """
    Finds the best ID matches for a batch of text snippets across different entity types in a single AI call.
    """
    if not items_to_match:
        return {}

    instructor_client = instructor.patch(client)

    # Bygg en flat liste over alle unike oppgaver for AI-en
    tasks_list = []
    for entity_type, texts in items_to_match.items():
        for text in texts:
            tasks_list.append({"text": text, "entity_type": entity_type})

    system_prompt = """
    You are an expert in high-throughput entity resolution. Your task is to process a batch of text snippets and find the single best matching entity for each from a provided database of valid entities.
    The provided lists of entities are the ONLY source of truth.
    For each snippet, you must return its original text, its entity type, the ID of the best match, and your reasoning.
    If no good match is found for a snippet, you MUST return null for its best_match_id.
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

        # Konverter svaret til et lett-brukbart oppslagskart
        id_lookup_map = {}
        for match in response.matches:
            if match.best_match_id:
                if match.entity_type not in id_lookup_map:
                    id_lookup_map[match.entity_type] = {}
                id_lookup_map[match.entity_type][match.input_text] = match.best_match_id
                print(f"  - [BATCH MATCHER] Matched '{match.input_text}' ({match.entity_type}) -> ID: {match.best_match_id}")

        return id_lookup_map
            
    except Exception as e:
        print(f"  - [BATCH MATCHER] CRITICAL ERROR during batch entity matching: {e}")
        return {}