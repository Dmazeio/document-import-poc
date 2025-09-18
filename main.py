# File: main.py (MODIFISERT FOR KOMPAKT JSON-LOGG)

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import time
# Vi trenger ikke lenger sys eller StringIO
# import sys
# from io import StringIO

# ... (alle de andre importene dine er de samme)
from src.document_converter import convert_file_to_markdown
from src.schema_processor import process_template_hierarchically
from src.openai_extractor import extract_data_with_hierarchy
from src.json_transformer import transform_to_dmaze_format_hierarchically
from src.document_classifier import classify_document_type
from src.document_splitter import split_document_into_items

# --- KONFIGURASJON ---
# ... (uendret)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Could not find OPENAI_API_KEY. Check your .env file.")
client = OpenAI(api_key=api_key)


### ENDRING: Forenklet logg-funksjon som lager en kompakt streng ###
def log_step(processing_log, step_name, function_to_run):
    """
    Kjører en funksjon, printer detaljer til konsollen, og legger til
    en kompakt en-linjes oppsummering i 'processing_log'-ordboken.
    """
    print(f"\n--- Running Step: {step_name} ---")
    start_time = time.time()
    status = "Pending"
    details = ""
    
    try:
        # Funksjonen kjøres, og dens interne print-setninger går rett til konsollen
        result = function_to_run()
        if isinstance(result, dict) and "error" in result:
            raise ValueError(result["error"])
        
        status = "Success"
        return result

    except Exception as e:
        status = "Failure"
        details = str(e) # Fanger opp feilmeldingen
        raise e

    finally:
        duration = time.time() - start_time
        duration_str = f"{duration:.2f}s"
        
        # Bygg den kompakte logg-strengen
        if status == "Failure":
            summary_string = f"Failure ({duration_str}): {details}"
        else:
            summary_string = f"Success ({duration_str})"
        
        # Legg den til i ordboken
        processing_log[step_name] = summary_string
        
        # Print en enkel oppsummering til konsollen
        print(f"  - Step Summary for {step_name}: {status} ({duration_str})")


# --- HOVEDLOGIKKEN I PROGRAMMET ---
if __name__ == "__main__":
    input_file_path = "input_documents/sample_4.docx"
    template_file_path = "input-schemas/Minutes of Meeting.json"
    
    os.makedirs("output", exist_ok=True)

    try:
        # Loggen er nå en ordbok (dictionary), ikke en liste
        initial_log = {} 
        
        schema_package = log_step(initial_log, "Template Processing", 
                                  lambda: process_template_hierarchically(template_file_path))
        root_object_name = schema_package['schema_tree']['name']

        markdown_content = log_step(initial_log, "Document Conversion", 
                                    lambda: convert_file_to_markdown(input_file_path))

        doc_type = log_step(initial_log, "Document Classification", 
                            lambda: classify_document_type(client, markdown_content, root_object_name))
        
        if doc_type == "multiple_items":
            item_chunks = log_step(initial_log, "Document Splitting", 
                                   lambda: split_document_into_items(client, markdown_content, root_object_name))
            
            print(f"\n--- Found {len(item_chunks)} items. Processing and saving each one individually. ---")
            
            for i, chunk in enumerate(item_chunks):
                print(f"\n{'='*20} PROCESSING ITEM {i+1}/{len(item_chunks)}: '{chunk.item_title}' {'='*20}")
                
                # Hvert element får sin egen logg ved å kopiere den initielle loggen
                item_log = initial_log.copy()
                item_summary = {
                    "inputFile": input_file_path, "templateUsed": template_file_path,
                    "overallStatus": "Pending", "itemTitle": chunk.item_title,
                    "processingTimestamp": datetime.now().isoformat(),
                    "processingLog": item_log # Bruker den nye ordboken
                }
                item_final_data = []

                try:
                    nested_data = log_step(item_log, "AI Data Extraction", 
                                           lambda: extract_data_with_hierarchy(client, chunk.item_content, schema_package))
                    item_final_data = log_step(item_log, "Data Transformation", 
                                               lambda: transform_to_dmaze_format_hierarchically(client, nested_data, schema_package))
                    item_summary["overallStatus"] = "Success"
                except Exception as e:
                    item_summary["overallStatus"] = "Failure"
                finally:
                    final_output = {"summary": item_summary, "dmaze_data": item_final_data}
                    safe_title = "".join(x for x in chunk.item_title if x.isalnum())[:50] or f"item_{i+1}"
                    item_output_path = f"output/{safe_title}_dmaze_import.json"
                    
                    print(f"\n--- Writing final log for '{chunk.item_title}' to {item_output_path} ---")
                    with open(item_output_path, "w", encoding="utf-8") as f:
                        json.dump(final_output, f, indent=4, ensure_ascii=False)

        else: # single_item
            summary_log = {
                "inputFile": input_file_path, "templateUsed": template_file_path,
                "overallStatus": "Pending", "processingTimestamp": datetime.now().isoformat(),
                "processingLog": initial_log # Bruker den nye ordboken
            }
            final_flat_data = []

            try:
                nested_data = log_step(initial_log, "AI Data Extraction", 
                                       lambda: extract_data_with_hierarchy(client, markdown_content, schema_package))
                final_flat_data = log_step(initial_log, "Data Transformation", 
                                           lambda: transform_to_dmaze_format_hierarchically(client, nested_data, schema_package))
                summary_log["overallStatus"] = "Success"
            except Exception as e:
                summary_log["overallStatus"] = "Failure"
            finally:
                final_output = {"summary": summary_log, "dmaze_data": final_flat_data}
                output_filename = os.path.splitext(os.path.basename(input_file_path))[0]
                output_file_path = f"output/{output_filename}_dmaze_import.json"
                print(f"\n--- Writing final log to {output_file_path} ---")
                with open(output_file_path, "w", encoding="utf-8") as f:
                    json.dump(final_output, f, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"\nCRITICAL FAILURE during initial setup. No files will be generated. Error: {e}")

    print("\n--- Processing finished. ---")