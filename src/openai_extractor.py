import json
from openai import OpenAI


def extract_data_with_hierarchy(client: OpenAI, document_text: str, schema_package: dict) -> dict:
    json_schema = schema_package['json_schema_for_api']

    system_prompt = """
    You are an expert assistant who analyzes documents and extracts key information.
    Structure the extracted content into the JSON format specified by the provided schema.
    If you cannot find information for a field, use `null`. Do not invent information.
    Title can not be null.
    For any datetime fields, format them as ISO 8601 strings (YYYY-MM-DDTHH:MM:SSZ).
    For any fields that contain people's names (like attendees or responsible persons),
    you MUST extract ONLY their full name.
    """

    user_prompt = f"Please extract the data from the following document based on the required schema.\n\nDOCUMENT TEXT:\n---\n{document_text}\n---"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
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