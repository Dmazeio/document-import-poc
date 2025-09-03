# File: main.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# CHANGE: Import the new function from the renamed file
from src.document_converter import convert_file_to_markdown
from src.schema_processor import process_template_hierarchically
from src.openai_extractor import extract_data_with_hierarchy
from src.json_transformer import transform_to_dmaze_format_hierarchically

# --- CONFIGURATION ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Could not find OPENAI_API_KEY. Check your .env file.")
client = OpenAI(api_key=api_key)


# --- MAIN LOGIC ---
if __name__ == "__main__":
    # You can easily change the file here to test different documents
    input_file_path = "input_documents/Sample_3.docx"
    template_file_path = "meeting_template.json"
    
    # Create the output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_file_path))[0]
    output_file_path = f"output/{base_name}_dmaze_import.json"

    # STEP 0: Process the template to create the schema tree
    print(f"--- Step 0: Processing template: {template_file_path} ---")
    schema_tree = process_template_hierarchically(template_file_path)
    
    if "error" in schema_tree:
        print(f"CRITICAL ERROR: {schema_tree['error']}")
    else:
        print("Template processed successfully. Starting document processing...")
        
        # STEP 1: CONVERT FILE TO MARKDOWN
        print(f"--- Step 1: Converting file to Markdown: {input_file_path} ---")
        
        # CHANGE: Call the new function and use a more descriptive variable name
        markdown_content = convert_file_to_markdown(input_file_path)
        
        if isinstance(markdown_content, dict) and "error" in markdown_content:
            print(f"ERROR: {markdown_content['error']}")
        else:
            print("File converted to Markdown successfully.")
            
            # STEP 2: SEND TO OPENAI
            print("--- Step 2: Sending Markdown to OpenAI for hierarchical analysis... ---")
            
            # CHANGE: Pass the new Markdown content along
            nested_data = extract_data_with_hierarchy(client, markdown_content, schema_tree)
            
            if "error" in nested_data:
                print(f"ERROR: {nested_data['error']}")
            else:
                print("AI analysis complete.")
                
                # STEP 3: TRANSFORM TO DMAZE FORMAT
                print("--- Step 3: Transforming data to Dmaze format... ---")
                final_flat_data = transform_to_dmaze_format_hierarchically(nested_data, schema_tree)
                
                # STEP 4: SAVE AND DISPLAY RESULT
                print(f"Transformation complete. Saving to: {output_file_path}")
                with open(output_file_path, "w", encoding="utf-8") as f:
                    json.dump(final_flat_data, f, indent=4, ensure_ascii=False)
                
                print("\n--- FINAL DMAZE IMPORT JSON ---")
                print(json.dumps(final_flat_data, indent=2, ensure_ascii=False))