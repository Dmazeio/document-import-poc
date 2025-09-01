import os
import json
import pdfplumber
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

# --- CONFIGURATION ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Could not find OPENAI_API_KEY. Check your .env file.")
client = OpenAI(api_key=api_key)


# --- HELPER FUNCTIONS ---

def is_valid_iso_datetime(dt_string):
    """Checks if a string is a valid ISO 8601 timestamp with a timezone."""
    if not isinstance(dt_string, str):
        return False
    try:
        # Tries to parse with a timezone, and then with 'Z' for UTC
        if dt_string.endswith('Z'):
            datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        else:
            datetime.fromisoformat(dt_string)
        return True
    except ValueError:
        return False

def extract_text_from_pdf(file_path):
    """Extracts all text from a PDF file."""
    print(f"Reading text from PDF file: {file_path}...")
    try:
        full_text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n\n"
        return full_text
    except FileNotFoundError:
        return {"error": f"The file was not found at the path: {file_path}"}
    except Exception as e:
        return {"error": f"An error occurred while reading the PDF: {e}"}

# --- CORE FUNCTIONS ---

def load_and_prepare_schema(schema_path):
    """
    Loads a JSON schema file and builds an instruction for OpenAI.
    Overrides the description for 'datetime' fields to avoid confusion.
    """
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
            # If the field is of type 'datetime', we ignore the potentially
            # misleading description from the JSON file and create our own.
            if field['type'] == 'datetime':
                # Uses 'label' for a more user-friendly description (e.g., "Start Time")
                label = field.get('label', field['fieldname'])
                custom_description = f"Extract the {label}. The final result must be a full ISO 8601 string (YYYY-MM-DDTHH:MM:SS±hh:mm)."
                desc_line = f"{i+1}. '{field['fieldname']}': {custom_description}"
            else:
                # For all other fields, we use the description from the file as usual.
                description_from_file = field.get('description', 'No description.')
                desc_line = f"{i+1}. '{field['fieldname']}': {description_from_file}"
            
            field_descriptions.append(desc_line)
        
        prepared_schema["field_instructions"] = "\n    ".join(field_descriptions)
        return prepared_schema
        
    except FileNotFoundError:
        return {"error": f"The schema file was not found at the path: {schema_path}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred while loading the schema: {e}"}

def extract_data_based_on_schema(text_content, schema_info):
    """Sends text to OpenAI and requests structured JSON based on a dynamic schema."""
    
    system_instruction = f"""
    You are an expert at analyzing documents and structuring data according to a strict schema.
    Analyze the user's text and extract data for the following fields:
    {schema_info['field_instructions']}

    IMPORTANT RULES FOR DATE AND TIME:
    - For datetime fields, you often need to combine a date (e.g., "3.21.07") with a time (e.g., "6:02pm") found in different places in the text.
    - Convert dates with two-digit years (like '07') to a four-digit year in the 21st century (2007).
    - Convert times with AM/PM to 24-hour format.
    - If no timezone is specified in the text, assume the timezone is UTC and use 'Z' at the end of the string. Example: "2007-03-21T18:02:00Z".

    GENERAL RULES:
    - The response MUST be a valid JSON object.
    - The JSON object MUST ONLY contain the keys: {json.dumps(schema_info['expected_keys'])}.
    - If a value for a field absolutely cannot be found, return `null` for that field.
    
    Respond ONLY with the JSON object itself.
    """

    try:
        print("Sending text to OpenAI for analysis based on schema...")
        response = client.chat.completions.create(
            # Using gpt-4o as it is the recommended model for this task.
            model="gpt-4o", 
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": text_content}
            ]
        )
        json_response_str = response.choices[0].message.content
        data = json.loads(json_response_str)
        
        # Validation
        if sorted(data.keys()) != sorted(schema_info['expected_keys']):
            return {"error": f"The response did not follow the schema. Expected keys: {schema_info['expected_keys']}, Received: {list(data.keys())}"}
        
        for field_name in schema_info['datetime_fields']:
            dt_value = data.get(field_name)
            if dt_value is not None and not is_valid_iso_datetime(dt_value):
                return {"error": f"The value for '{field_name}' ('{dt_value}') is not in the correct ISO 8601 format."}

        # Post-processing
        start_field = 'startuptime'
        end_field = 'endtime'
        if start_field in data and end_field in data:
            start_dt = data.get(start_field)
            end_dt = data.get(end_field)
            if start_dt and not end_dt:
                data[end_field] = start_dt
                print(f"Info: '{end_field}' not found. Setting it to the same value as '{start_field}'.")
            elif end_dt and not start_dt:
                data[start_field] = end_dt
                print(f"Info: '{start_field}' not found. Setting it to the same value as '{end_field}'.")
            
        return data

    except json.JSONDecodeError:
        return {"error": "Failed to decode the JSON response from OpenAI."}
    except Exception as e:
        return {"error": f"An error occurred during the call to OpenAI: {e}"}


# --- MAIN LOGIC ---
if __name__ == "__main__":
    pdf_file_path = "Minutes_of_meeting_samples/SampleMinutes-1.pdf"
    schema_file_path = "meeting_template.json"
    
    schema_info = load_and_prepare_schema(schema_file_path)
    if "error" in schema_info:
        print(f"CRITICAL ERROR: {schema_info['error']}")
    else:
        raw_text_from_pdf = extract_text_from_pdf(pdf_file_path)
        
        if "error" in raw_text_from_pdf:
            print(f"Error: {raw_text_from_pdf['error']}")
        else:
            print("Text successfully extracted from PDF.")
            structured_data = extract_data_based_on_schema(raw_text_from_pdf, schema_info)
            
            print("\n--- Result from OpenAI (validated against schema) ---")
            print(json.dumps(structured_data, indent=2, ensure_ascii=False))
            print("-------------------------------------------------")