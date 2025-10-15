import json
from .ai_client import AIClient

def extract_data_with_hierarchy(ai_client: AIClient, document_text: str, schema_package: dict) -> dict:
    """Extracts structured data from text using the centralized AIClient."""
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

    # Define the response format for OpenAI's native JSON schema mode
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "dmaze_import_schema",
            "schema": json_schema,
            "strict": True
        }
    }

    try:
        # Use the single, unified method from AIClient
        return ai_client.get_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format_options=response_format,
            model="gpt-5" # Assuming this model supports the advanced JSON mode
        )
    except Exception as e:
        return {"error": f"An unexpected error occurred during the AI call: {e}"}