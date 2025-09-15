# File: main.py (FULLY GENERALIZED VERSION)

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

from src.document_converter import convert_file_to_markdown
from src.schema_processor import process_template_hierarchically
from src.openai_extractor import extract_data_with_hierarchy
from src.json_transformer import transform_to_dmaze_format_hierarchically
# Importer de oppdaterte funksjonene
from src.document_classifier import classify_document_type
from src.document_splitter import split_document_into_items

 
# --- CONFIGURATION ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Could not find OPENAI_API_KEY. Check your .env file.")
client = OpenAI(api_key=api_key)


# --- MAIN LOGIC ---
if __name__ == "__main__":
    input_file_path = "input_documents/sample_4.docx"
    template_file_path = "input-schemas/Minutes of Meeting.json"
    
    os.makedirs("output", exist_ok=True)

    # STEP 0: Prosesser malen
    print(f"--- Step 0: Processing template: {template_file_path} ---")
    schema_package = process_template_hierarchically(template_file_path)    #->  Schema processor filen 1 
  
    if "error" in schema_package:
        print(f"CRITICAL ERROR processing template: {schema_package['error']}")
    else:
        # Hent navnet på rot-objektet for å gi kontekst til AI-en
        root_object_name = schema_package['schema_tree']['name']

        # STEP 1: Konverter til Markdown
        print(f"\n--- Step 1: Converting file to Markdown: {input_file_path} ---")
        markdown_content = convert_file_to_markdown(input_file_path) #->  Document converter filen (5)
        
        if isinstance(markdown_content, dict) and "error" in markdown_content:
            print(f"ERROR: {markdown_content['error']}")
        else:
            print("File converted to Markdown successfully.")
            
            # STEP 2: Klassifiser dokumentet på en generell måte
            print("\n--- Step 2: Classifying document structure... ---")
            doc_type = classify_document_type(client, markdown_content, root_object_name) #->  Document classifier filen (6)

            # STEP 3: Betinget ruting basert på generell struktur
            if doc_type == "multiple_items":
                print("\n--- Step 3: Document contains multiple items. Splitting into chunks... ---")
                item_chunks = split_document_into_items(client, markdown_content, root_object_name) #->  Document splitter filen (7)
                
                if not item_chunks:
                    print("Processing stopped: No items were found or an error occurred during splitting.")
                else:
                    print(f"Found {len(item_chunks)} items. Processing each one...")
                    for i, chunk in enumerate(item_chunks):
                        print(f"\n--- Processing Item {i+1}/{len(item_chunks)}: '{chunk.item_title}' ---")
                        
                        nested_data = extract_data_with_hierarchy(client, chunk.item_content, schema_package)
                        
                        if "error" in nested_data:
                            print(f"  ERROR: Could not process chunk for '{chunk.item_title}': {nested_data['error']}")
                            continue
                        
                        final_flat_data = transform_to_dmaze_format_hierarchically(
                            client, nested_data, schema_package
                        )
                        
                        safe_title = "".join(x for x in chunk.item_title if x.isalnum())[:50]
                        output_file_path = f"output/{safe_title}_dmaze_import.json"
                        
                        print(f"  - Saving result to {output_file_path}")
                        with open(output_file_path, "w", encoding="utf-8") as f:
                            json.dump(final_flat_data, f, indent=4, ensure_ascii=False)
                        
                        print(f"\n--- FINAL DMAZE IMPORT JSON (for item '{chunk.item_title}') ---")
                        print(json.dumps(final_flat_data, indent=2, ensure_ascii=False))

            else: # doc_type == "single_item"
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


        