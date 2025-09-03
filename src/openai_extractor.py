# File: src/openai_extractor.py
import json
from openai import OpenAI

# WE DON'T NEED THIS FUNCTION ANYMORE!
# def generate_prompt_from_schema_tree(node: dict) -> str: ...

def extract_data_with_hierarchy(client: OpenAI, document_text: str, schema_package: dict) -> dict:
    """
    Uses a dynamically generated, strict JSON Schema to extract a deeply
    nested JSON structure from a document.
    """
    # Get the two parts we created in the processor
    schema_tree = schema_package['schema_tree']
    json_schema = schema_package['json_schema_for_api']

    # The prompt can now be much simpler!
    # We no longer need to explain the structure, just the task.
    system_prompt = """
    You are an expert assistant who analyzes documents and extracts key information.
    Structure the extracted content into the JSON format specified by the provided schema.
    If you cannot find information for a field, use `null`.
    For any datetime fields, format them as ISO 8601 strings (YYYY-MM-DDTHH:MM:SSZ).
    """

    user_prompt = f"Please extract the data from the following document based on the required schema.\n\nDOCUMENT TEXT:\n---\n{document_text}\n---"

    try:
        response = client.chat.completions.create(
            model="gpt-5",
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "dmaze_import_schema",
                    "schema": json_schema,
                    "strict": True  
                }
            },
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": f"An unexpected error occurred during the AI call: {e}"}