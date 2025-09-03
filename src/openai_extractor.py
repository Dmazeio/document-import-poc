# File: src/openai_extractor.py

import json
from openai import OpenAI

def extract_nested_data_dynamically(client: OpenAI, document_text: str, schema_metadata: dict) -> dict:
    """
    Uses a dynamically generated prompt based on metadata from the template
    to extract a nested JSON structure.
    """
    parent_name = schema_metadata['parent_name']
    child_name = schema_metadata['child_name']
    
    system_prompt = f"""
    You are an expert assistant who analyzes documents and structures content into a nested JSON format.

    RULES:
    1.  You MUST respond with a single, valid JSON object.
    2.  The JSON object must have two top-level keys: "{parent_name}" and "{child_name}".
    3.  "{parent_name}" must be an object containing the main details for the meeting. The fields to extract are: {json.dumps(schema_metadata['parent_fields'])}.
    4.  "{child_name}" must be a JSON array of objects. Each object represents an agenda item. The fields to extract for each item are: {json.dumps(schema_metadata['child_fields'])}.
    5.  For any datetime fields, you must format them as ISO 8601 strings (YYYY-MM-DDTHH:MM:SSZ).
    6.  If you cannot find information for a field, use `null`.
    7.  Respond ONLY with the JSON object.
    """

    user_prompt = f"Here is the text from the document. Please extract the data according to the rules.\n\nDOCUMENT TEXT:\n---\n{document_text}\n---"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": f"An unexpected error occurred during the AI call: {e}"}