# File: src/tools.py (TRULY GENERIC AI MATCHER)

import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

# Pydantic-modell for å sikre et pålitelig, strukturert svar fra AI-en
class BestMatch(BaseModel):
    best_match_id: Optional[str] = Field(
        ..., 
        description="The ID of the best matching entity from the provided list. If no confident match is found, this MUST be null."
    )
    confidence_score: float = Field(
        ...,
        description="A score from 0.0 to 1.0 indicating the confidence in the match."
    )
    reasoning: str = Field(
        ..., 
        description="A brief explanation for the choice, or why no match was found."
    )

def find_best_entity_match_with_ai(
    client: OpenAI, 
    text_to_match: str, 
    entity_list: List[Dict],
    entity_type: str,
    display_field: str, # NY PARAMETER: Hvilket felt skal AI-en se på?
    id_field: str      # NY PARAMETER: Hvilket felt inneholder ID-en?
) -> Optional[str]:
    """
    Bruker AI til å finne den beste matchen for en tekst i en liste med entiteter,
    styrt av metadata fra API-et.
    """
    if not text_to_match or not entity_list:
        return None

    instructor_client = instructor.patch(client)
    
    # Prompten er nå 100% dynamisk og bruker instruksjonene fra API-et
    system_prompt = f"""
    You are an expert in entity resolution and data matching. Your task is to find the single best matching entity from a provided list based on a text snippet.
    The list provided is the ONLY source of truth.
    The '{display_field}' field is the most important for matching, but you should consider all available fields for context.
    You MUST return the value from the '{id_field}' field of the best matching entity.
    If there is no good match, you MUST return null for the best_match_id.
    """
    
    user_prompt = f"""
    Here is the list of available entities of type '{entity_type}':
    --- AVAILABLE ENTITIES ---
    {entity_list}
    --- END OF LIST ---

    Here is the text snippet to match:
    --- TEXT TO MATCH ---
    "{text_to_match}"
    --- END OF TEXT ---

    Find the best matching entity and return its '{id_field}'.
    """
    
    try:
        match_result = instructor_client.chat.completions.create(
            model="gpt-4o",
            response_model=BestMatch,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_retries=1
        )
        
        print(f"  - [AI MATCHER] Matched '{text_to_match}' -> ID: {match_result.best_match_id} (Confidence: {match_result.confidence_score:.2f}). Reason: {match_result.reasoning}")
        
        # Setter en terskel for å kun returnere svar vi er trygge på
        if match_result.best_match_id and match_result.confidence_score > 0.7:
            return match_result.best_match_id
        else:
            if match_result.best_match_id: # Hvis ID ble funnet, men konfidens er for lav
                print(f"  - [AI MATCHER] Match confidence ({match_result.confidence_score:.2f}) was below threshold 0.7. Discarding match.")
            return None
            
    except Exception as e:
        print(f"  - [AI MATCHER] CRITICAL ERROR during entity matching: {e}")
        return None