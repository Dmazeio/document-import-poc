import json
from datetime import datetime
from openai import OpenAI

# --- HELPER FUNCTIONS (used only by the AI logic) ---

def is_valid_iso_datetime(dt_string: str) -> bool:
    """Checks if a string is a valid ISO 8601 timestamp."""
    if not isinstance(dt_string, str):
        return False
    try:
        # Uses fromisoformat which is built for this purpose
        datetime.fromisoformat(dt_string)
        return True
    except ValueError:
        return False

# --- CORE FUNCTIONS (everything related to AI and schema) ---

def load_and_prepare_schema(schema_path: str) -> dict:
    """Loads a JSON schema file and prepares it for use with OpenAI."""
    print(f"Loading and preparing schema from: {schema_path}...")
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)

        prepared_schema = {
            "fields": schema.get("fields", []),
            "expected_keys": [field["fieldname"] for field in schema.get("fields", [])],
            "datetime_fields": [field["fieldname"] for field in schema.get("fields", []) if field["type"] == "datetime"]
        }

        field_descriptions = []
        for i, field in enumerate(prepared_schema["fields"]):
            desc = f"{i+1}. '{field['fieldname']}': {field.get('description', 'No description.')}"
            if field['type'] == 'datetime':
                desc += " This MUST be formatted as an ISO 8601 string (YYYY-MM-DDTHH:MM:SSZ)." # Use Z for UTC
            field_descriptions.append(desc)
        
        prepared_schema["field_instructions"] = "\n    ".join(field_descriptions)
        return prepared_schema
        
    except Exception as e:
        return {"error": f"An unexpected error occurred while loading the schema: {e}"}

def extract_data_based_on_schema(client: OpenAI, text_content: str, schema_info: dict) -> dict:
    """Sends text to OpenAI and requests structured JSON based on a dynamic schema."""
    system_instruction = f"""
    You are an expert at analyzing documents and structuring data according to a strict schema.
    Analyze the user's text and extract data for the following fields:
    {schema_info['field_instructions']}

    IMPORTANT RULES:
    - The response MUST be a valid JSON object.
    - The JSON object MUST ONLY contain the keys: {json.dumps(schema_info['expected_keys'])}.
    - If a value for a field is not found, you MUST return `null` for that field.

    Respond ONLY with the JSON object itself.
    """

    try:
        print("Sending text to OpenAI for schema-based analysis...")
        response = client.chat.completions.create(
            model="gpt-4o", 
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": text_content}
            ]
        )
        data = json.loads(response.choices[0].message.content)
        
        # Validation of keys
        if sorted(data.keys()) != sorted(schema_info['expected_keys']):
            return {"error": f"The response did not follow the schema. Expected keys: {schema_info['expected_keys']}, Received: {list(data.keys())}"}
        
        # Validation of datetime format
        for field_name in schema_info['datetime_fields']:
            dt_value = data.get(field_name)
            if dt_value is not None and not is_valid_iso_datetime(dt_value):
                return {"error": f"The value for '{field_name}' ('{dt_value}') is not in the correct ISO 8601 format."}

        return data

    except Exception as e:
        return {"error": f"An error occurred during the call to OpenAI: {e}"}