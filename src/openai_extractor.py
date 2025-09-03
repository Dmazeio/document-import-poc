# File: src/openai_extractor.py
import json
from openai import OpenAI

def generate_prompt_from_schema_tree(node: dict) -> str:
    """
    Recursively generates a string describing the expected JSON structure
    for the AI prompt.
    """
    prompt_part = f'- The top-level key must be "{node["name"]}", which is a JSON object.\n'
    prompt_part += f'- The fields for a "{node["name"]}" object are: {json.dumps(node["fields"])}.\n'

    for child in node.get("children", []):
        child_name = child["name"]
        prompt_part += f'- Inside a "{node["name"]}" object, there should be a key named "{child_name}".\n'
        prompt_part += f'- "{child_name}" must be a JSON array of objects.\n'
        # Recurse to describe the child structure
        prompt_part += generate_prompt_from_schema_tree(child).replace("- The top-level key must be", "  - Each object in the array represents a")

    return prompt_part


def extract_data_with_hierarchy(client: OpenAI, document_text: str, schema_tree: dict) -> dict:
    """
    Uses a dynamically generated prompt based on a hierarchical schema tree
    to extract a deeply nested JSON structure.
    """
    
    structure_rules = generate_prompt_from_schema_tree(schema_tree)

    system_prompt = f"""
    You are an expert assistant who analyzes documents and structures content into a deeply nested JSON format based on a specific schema.

    RULES:
    1.  You MUST respond with a single, valid JSON object.
    2.  If you cannot find information for a field, use `null`.
    3.  For any datetime fields, format them as ISO 8601 strings (YYYY-MM-DDTHH:MM:SSZ).
    4.  The required JSON structure is as follows:
    {structure_rules}
    5.  Respond ONLY with the JSON object. Do not add explanations.
    """

    user_prompt = f"Here is the text from the document. Please extract the data according to the rules and the specified nested structure.\n\nDOCUMENT TEXT:\n---\n{document_text}\n---"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        # The AI should return a JSON with the root key, e.g. {"mom": {...}}
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": f"An unexpected error occurred during the AI call: {e}"}