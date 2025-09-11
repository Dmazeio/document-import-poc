# File: main.py (FINAL CLEANED VERSION)

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Importer alle nødvendige moduler.
# schema_analyzer er nå fjernet.
from src.document_converter import convert_file_to_markdown
from src.schema_processor import process_template_hierarchically
from src.openai_extractor import extract_data_with_hierarchy
from src.json_transformer import transform_to_dmaze_format_hierarchically
from src.document_classifier import classify_document_type
from src.document_splitter import split_document_into_meetings

 
# --- CONFIGURATION ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Could not find OPENAI_API_KEY. Check your .env file.")
# 'client' er nøkkelkomponenten som sendes til transformeren for AI-matching.
client = OpenAI(api_key=api_key)


# --- MAIN LOGIC ---
if __name__ == "__main__":
    # Bytt disse linjene for å teste forskjellige maler og dokumenter
    input_file_path = "input_documents/risk_assessment_sample.txt"
    template_file_path = "input-schemas/Risk Assessment - Enterprise Risk Assessment.json"
    
    os.makedirs("output", exist_ok=True)

    # STEP 0: Prosesser malen for å bygge et internt "kart"
    print(f"--- Step 0: Processing template: {template_file_path} ---")
    schema_package = process_template_hierarchically(template_file_path) 
    
    if "error" in schema_package:
        print(f"CRITICAL ERROR processing template: {schema_package['error']}")
    else:
        # STEP 1: Konverter input-dokument til ren tekst
        print(f"\n--- Step 1: Converting file to Markdown: {input_file_path} ---")
        markdown_content = convert_file_to_markdown(input_file_path)
        
        if isinstance(markdown_content, dict) and "error" in markdown_content:
            print(f"ERROR: {markdown_content['error']}")
        else:
            print("File converted to Markdown successfully.")
            
            # STEP 2: Klassifiser dokumentstrukturen
            print("\n--- Step 2: Classifying document structure... ---")
            doc_type = classify_document_type(client, markdown_content)

            # STEP 3: Betinget ruting basert på dokumenttype
            if doc_type == "multiple_meetings":
                print("\n--- Step 3: Document contains multiple items. Splitting... ---")
                meeting_chunks = split_document_into_meetings(client, markdown_content)
                
                if not meeting_chunks:
                    print("Processing stopped: No items were found.")
                else:
                    print(f"Found {len(meeting_chunks)} items. Processing each one...")
                    for i, chunk in enumerate(meeting_chunks):
                        print(f"\n--- Processing Item {i+1}/{len(meeting_chunks)}: '{chunk.meeting_title}' ---")
                        
                        nested_data = extract_data_with_hierarchy(client, chunk.meeting_content, schema_package)
                        
                        if "error" in nested_data:
                            print(f"  ERROR: Could not process chunk for '{chunk.meeting_title}': {nested_data['error']}")
                            continue
                        
                        final_flat_data = transform_to_dmaze_format_hierarchically(
                            client, nested_data, schema_package
                        )
                        
                        safe_title = "".join(x for x in chunk.meeting_title if x.isalnum())[:50]
                        output_file_path = f"output/{safe_title}_dmaze_import.json"
                        
                        print(f"  - Saving result to {output_file_path}")
                        with open(output_file_path, "w", encoding="utf-8") as f:
                            json.dump(final_flat_data, f, indent=4, ensure_ascii=False)
                        
                        print(f"\n--- FINAL DMAZE IMPORT JSON (for item '{chunk.meeting_title}') ---")
                        print(json.dumps(final_flat_data, indent=2, ensure_ascii=False))

            else: # doc_type == "single_meeting"
                print("\n--- Step 3: Document contains a single item. Processing directly... ---")
                
                nested_data = extract_data_with_hierarchy(client, markdown_content, schema_package)
                
                if "error" in nested_data:
                    print(f"ERROR: Could not process single item document: {nested_data['error']}")
                else:
                    final_flat_data = transform_to_dmaze_format_hierarchically(
                        client, nested_data, schema_package
                    )
                    
                    base_name = os.path.splitext(os.path.basename(input_file_path))[0]
                    output_file_path = f"output/{base_name}_dmaze_import.json"
                    
                    print(f"  - Saving result to {output_file_path}")
                    with open(output_file_path, "w", encoding="utf-8") as f:
                        json.dump(final_flat_data, f, indent=4, ensure_ascii=False)

                    print("\n--- FINAL DMAZE IMPORT JSON ---")
                    print(json.dumps(final_flat_data, indent=2, ensure_ascii=False))

            print("\n--- Processing finished. ---")