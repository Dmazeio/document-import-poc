# main.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Import the functions from your new files!
from src.pdf_processor import extract_text_from_pdf
from src.openai_extractor import load_and_prepare_schema, extract_data_based_on_schema

# --- CONFIGURATION ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Could not find OPENAI_API_KEY. Check your .env file.")
client = OpenAI(api_key=api_key)


# --- MAIN LOGIC ---
if __name__ == "__main__":
    pdf_file_path = "input_documents/SampleMinutes-1.pdf"
    schema_file_path = "meeting_template.json"
    
    # Step 1: Load and prepare the schema
    schema_info = load_and_prepare_schema(schema_file_path)
    if "error" in schema_info:
        print(f"CRITICAL ERROR: {schema_info['error']}")
    else:
        # Step 2: Extract text from the PDF
        raw_text = extract_text_from_pdf(pdf_file_path)
        
        if isinstance(raw_text, dict) and "error" in raw_text:
            print(f"Error: {raw_text['error']}")
        else:
            print("Text was successfully extracted from the PDF.")
            
            # Step 3: Extract structured data based on the schema
            structured_data = extract_data_based_on_schema(client, raw_text, schema_info)
            
            print("\n--- Result from OpenAI (validated against schema) ---")
            print(json.dumps(structured_data, indent=2, ensure_ascii=False))
            print("-------------------------------------------------")