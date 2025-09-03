# File: main.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Import all the functions you need from the other files
from src.pdf_processor import extract_text_from_pdf
from src.schema_processor import process_template
from src.openai_extractor import extract_nested_data_dynamically
from src.json_transformer import transform_to_dmaze_format_dynamically

# --- CONFIGURATION ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Could not find OPENAI_API_KEY. Check your .env file.")
client = OpenAI(api_key=api_key)


# --- MAIN LOGIC ---
if __name__ == "__main__":
    pdf_file_path = "input_documents/SampleMinutes-1.pdf"
    template_file_path = "meeting_template.json" # Define the path to the template
    
    # Create the output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    base_name = os.path.splitext(os.path.basename(pdf_file_path))[0]
    output_file_path = f"output/{base_name}_dmaze_import.json"

    # STEP 0: Process the template to create the "recipe" (metadata)
    print(f"--- Step 0: Processing template: {template_file_path} ---")
    schema_metadata = process_template(template_file_path)
    
    # Check for errors from the template processing before continuing
    if "error" in schema_metadata:
        print(f"CRITICAL ERROR: {schema_metadata['error']}")
    else:
        print("Template processed successfully. Starting document processing...")
        
        # Step 1: Extract text from the PDF
        print(f"--- Step 1: Extracting text from: {pdf_file_path} ---")
        raw_text = extract_text_from_pdf(pdf_file_path)
        if isinstance(raw_text, dict) and "error" in raw_text:
            print(f"ERROR: {raw_text['error']}")
        else:
            print("Text extracted successfully.")
            
            # Step 2: Get nested data from OpenAI (sending metadata)
            print("--- Step 2: Sending text to OpenAI for analysis... ---")
            nested_data = extract_nested_data_dynamically(client, raw_text, schema_metadata)
            
            if "error" in nested_data:
                print(f"ERROR: {nested_data['error']}")
            else:
                print("AI analysis complete.")
                
                # Step 3: Transform data to Dmaze format (sending metadata)
                print("--- Step 3: Transforming data to Dmaze format... ---")
                final_flat_data = transform_to_dmaze_format_dynamically(nested_data, schema_metadata)
                
                # Step 4: Save and display the result
                print(f"Transformation complete. Saving to: {output_file_path}")
                with open(output_file_path, "w", encoding="utf-8") as f:
                    json.dump(final_flat_data, f, indent=4, ensure_ascii=False)
                
                print("\n--- FINAL DMAZE IMPORT JSON (Dynamically generated) ---")
                print(json.dumps(final_flat_data, indent=2, ensure_ascii=False))