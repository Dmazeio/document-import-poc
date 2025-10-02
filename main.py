import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import time

from src.document_converter import convert_file_to_markdown
from src.schema_processor import process_template_hierarchically
from src.openai_extractor import extract_data_with_hierarchy
from src.json_transformer import transform_to_dmaze_format_hierarchically
from src.document_classifier import classify_document_type
from src.document_splitter import split_document_into_items

# --- CONFIGURATION ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Could not find OPENAI_API_KEY. Check your .env file.")
client = OpenAI(api_key=api_key)


def log_step(processing_log: dict, step_name: str, function_to_run, errors_list: list):
    """
    Runs a function, prints details to the console, and adds
    a compact one-line summary to the 'processing_log' dictionary.
    Also collects error messages in errors_list.
    """
    print(f"\n--- Running Step: {step_name} ---")
    start_time = time.time()
    status = "Pending"
    details = ""
    result = None
    
    try:
        result = function_to_run()
        # Custom error handling for functions that return dict with 'error' key
        if isinstance(result, dict) and "error" in result:
            raise ValueError(result["error"])
        
        status = "Success"
        return result

    except Exception as e:
        status = "Failure"
        details = str(e)
        errors_list.append(f"Step '{step_name}' failed: {details}")
        raise e # Re-raise the exception to stop the current processing flow if critical

    finally:
        duration = time.time() - start_time
        duration_str = f"{duration:.2f}s"
        
        if status == "Failure":
            summary_string = f"Failure ({duration_str}): {details}"
        else:
            summary_string = f"Success ({duration_str})"
        
        processing_log[step_name] = summary_string
        print(f"  - Step Summary for {step_name}: {status} ({duration_str})")


def generate_human_readable_summary(summary_obj: dict, root_object_name: str, dmaze_data: list) -> str:
    """
    Generates a human-friendly summary of the import process for a given item or document.
    """
    overall_status = summary_obj.get("overallStatus", "Unknown status")
    input_file_basename = os.path.basename(summary_obj.get("inputFile", "unknown file"))
    template_basename = os.path.basename(summary_obj.get("templateUsed", "unknown template"))
    item_title = summary_obj.get("itemTitle")
    errors = summary_obj.get("errorsEncountered", [])
    warnings = summary_obj.get("warningsEncountered", []) # --- ADDED ---
    
    summary_parts = []

    # Initial statement about the processing
    if item_title:
        summary_parts.append(f"Summary of the import process for document part '{item_title}' from the file '{input_file_basename}', based on the template '{template_basename}'.")
    else:
        summary_parts.append(f"Summary of the import process for the document '{input_file_basename}', based on the template '{template_basename}'.")

    # --- MODIFIED: Overall status and what was generated ---
    if overall_status == "Success":
        summary_parts.append("\n**Overall status:** ✅ Success")
    elif overall_status == "SuccessWithWarnings":
        summary_parts.append("\n**Overall status:** ⚠️ Success, but with warnings requiring manual review.")
    else: # overall_status is Failure
        summary_parts.append("\n**Overall status:** ❌ Failure")

    if dmaze_data:
        num_dmaze_objects = len(dmaze_data)
        num_root_objects = sum(1 for obj in dmaze_data if obj.get('objectname') == root_object_name)
        
        if num_root_objects > 0:
            summary_parts.append(f"A total of {num_dmaze_objects} Dmaze objects were generated, of which {num_root_objects} are main objects of type '{root_object_name}'.")
        else:
            summary_parts.append(f"The process generated {num_dmaze_objects} Dmaze objects, but none of them are of the main type '{root_object_name}'. This might indicate a problem with the schema or extraction.")
    elif overall_status != "Failure":
        summary_parts.append("No Dmaze objects were generated, even though the technical process indicates success. This could be due to missing data in the document or a data extraction problem.")
    else:
        summary_parts.append("No Dmaze objects were generated due to errors in the process.")


    # What went well and what didn't
    successful_steps = [step for step, status in summary_obj.get("processingLog", {}).items() if "Success" in status]
    failed_steps = [step for step, status in summary_obj.get("processingLog", {}).items() if "Failure" in status]

    if successful_steps:
        summary_parts.append(f"\n**Successful steps:** {', '.join(successful_steps)}.")
    if failed_steps:
        summary_parts.append(f"**Failed steps:** {', '.join(failed_steps)}. See 'Errors Encountered' for details.")

    # --- ADDED: List specific warnings ---
    if warnings:
        summary_parts.append("\n**⚠️ Warnings (require manual review):**")
        for warning_msg in warnings:
            summary_parts.append(f"- {warning_msg}")

    # List specific errors
    if errors:
        summary_parts.append("\n**Errors Encountered:**")
        for error_msg in errors:
            summary_parts.append(f"- {error_msg}")
    
    # Only show this message if there was truly nothing to report
    if not errors and not warnings:
        summary_parts.append("\nNo specific errors or warnings were recorded during processing.")

    return "\n".join(summary_parts)


# --- MAIN PROGRAM LOGIC ---
if __name__ == "__main__":
    input_file_path = "input_documents/sample_4.docx"
    template_file_path = "input-schemas/Minutes of Meeting.json"
    
    os.makedirs("output", exist_ok=True)

    all_errors_during_run = []
    global_root_object_name = "unknown"

    try:
        initial_log = {} 
        
        schema_package = log_step(initial_log, "Template Processing", 
                                  lambda: process_template_hierarchically(template_file_path), all_errors_during_run)
        global_root_object_name = schema_package['schema_tree']['name']

        markdown_content = log_step(initial_log, "Document Conversion", 
                                    lambda: convert_file_to_markdown(input_file_path), all_errors_during_run)

        doc_type = log_step(initial_log, "Document Classification", 
                            lambda: classify_document_type(client, markdown_content, global_root_object_name), all_errors_during_run)
        
        if doc_type == "multiple_items":
            item_chunks = log_step(initial_log, "Document Splitting", 
                                   lambda: split_document_into_items(client, markdown_content, global_root_object_name), all_errors_during_run)
            
            print(f"\n--- Found {len(item_chunks)} items. Processing and saving each one individually. ---")
            
            for i, chunk in enumerate(item_chunks):
                print(f"\n{'='*20} PROCESSING ITEM {i+1}/{len(item_chunks)}: '{chunk.item_title}' {'='*20}")
                
                item_log = initial_log.copy()
                item_errors = all_errors_during_run.copy() 
                item_warnings = [] # --- ADDED ---
                
                item_summary = {
                    "inputFile": input_file_path, "templateUsed": template_file_path,
                    "overallStatus": "Pending", "itemTitle": chunk.item_title,
                    "processingTimestamp": datetime.now().isoformat(),
                    "processingLog": item_log,
                    "errorsEncountered": item_errors,
                    "warningsEncountered": item_warnings # --- ADDED ---
                }
                item_final_data = []

                try:
                    nested_data = log_step(item_log, "AI Data Extraction", 
                                           lambda: extract_data_with_hierarchy(client, chunk.item_content, schema_package), item_errors)
                    
                    # --- MODIFIED: Transformation step now returns a dict ---
                    transformation_result = log_step(item_log, "Data Transformation", 
                                               lambda: transform_to_dmaze_format_hierarchically(client, nested_data, schema_package), item_errors)
                    
                    item_final_data = transformation_result.get("dmaze_data", [])
                    item_warnings.extend(transformation_result.get("warnings", []))
                    
                    # --- MODIFIED: Set status based on warnings ---
                    if item_warnings:
                        item_summary["overallStatus"] = "SuccessWithWarnings"
                    else:
                        item_summary["overallStatus"] = "Success"

                except Exception:
                    item_summary["overallStatus"] = "Failure"
                finally:
                    item_summary["humanReadableSummary"] = generate_human_readable_summary(item_summary, global_root_object_name, item_final_data)

                    final_output = {"summary": item_summary, "dmaze_data": item_final_data}
                    safe_title = "".join(x for x in chunk.item_title if x.isalnum() or x in [' ', '-']).replace(' ', '_')[:50]
                    if not safe_title:
                        safe_title = f"item_{i+1}"
                    item_output_path = f"output/{safe_title}_dmaze_import.json"
                    
                    print(f"\n--- Writing final log for '{chunk.item_title}' to {item_output_path} ---")
                    with open(item_output_path, "w", encoding="utf-8") as f:
                        json.dump(final_output, f, indent=4, ensure_ascii=False)

        else: # single_item
            all_warnings_during_run = [] # --- ADDED ---
            summary_log = {
                "inputFile": input_file_path, "templateUsed": template_file_path,
                "overallStatus": "Pending", "processingTimestamp": datetime.now().isoformat(),
                "processingLog": initial_log,
                "errorsEncountered": all_errors_during_run,
                "warningsEncountered": all_warnings_during_run # --- ADDED ---
            }
            final_flat_data = []

            try:
                nested_data = log_step(initial_log, "AI Data Extraction", 
                                       lambda: extract_data_with_hierarchy(client, markdown_content, schema_package), all_errors_during_run)
                
                # --- MODIFIED: Transformation step now returns a dict ---
                transformation_result = log_step(initial_log, "Data Transformation", 
                                           lambda: transform_to_dmaze_format_hierarchically(client, nested_data, schema_package), all_errors_during_run)

                final_flat_data = transformation_result.get("dmaze_data", [])
                all_warnings_during_run.extend(transformation_result.get("warnings", []))
                
                # --- MODIFIED: Set status based on warnings ---
                if all_warnings_during_run:
                    summary_log["overallStatus"] = "SuccessWithWarnings"
                else:
                    summary_log["overallStatus"] = "Success"

            except Exception:
                summary_log["overallStatus"] = "Failure"
            finally:
                summary_log["humanReadableSummary"] = generate_human_readable_summary(summary_log, global_root_object_name, final_flat_data)

                final_output = {"summary": summary_log, "dmaze_data": final_flat_data}
                output_filename = os.path.splitext(os.path.basename(input_file_path))[0]
                output_file_path = f"output/{output_filename}_dmaze_import.json"
                print(f"\n--- Writing final log to {output_file_path} ---")
                with open(output_file_path, "w", encoding="utf-8") as f:
                    json.dump(final_output, f, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"\nCRITICAL ERROR during initial setup or main process. Error: {e}")
        if 'summary_log' not in locals():
            summary_log = {
                "inputFile": input_file_path, "templateUsed": template_file_path,
                "overallStatus": "Failure", "processingTimestamp": datetime.now().isoformat(),
                "processingLog": initial_log if 'initial_log' in locals() else {},
                "errorsEncountered": all_errors_during_run,
                "warningsEncountered": [] # Add for schema consistency
            }
        
        if not all_errors_during_run or not any("CRITICAL ERROR" in err for err in all_errors_during_run):
            all_errors_during_run.append(f"CRITICAL ERROR: {e}")
        
        summary_log["overallStatus"] = "Failure"
        summary_log["errorsEncountered"] = all_errors_during_run
        summary_log["humanReadableSummary"] = generate_human_readable_summary(summary_log, global_root_object_name, [])

        output_filename = os.path.splitext(os.path.basename(input_file_path))[0]
        output_file_path = f"output/{output_filename}_dmaze_import_CRITICAL_ERROR.json"
        print(f"\n--- Attempting to write partial log for critical error to {output_file_path} ---")
        try:
            with open(output_file_path, "w", encoding="utf-8") as f:
                json.dump({"summary": summary_log, "dmaze_data": []}, f, indent=4, ensure_ascii=False)
        except Exception as file_write_e:
            print(f"Could not write critical error log: {file_write_e}")

    print("\n--- Processing is complete. ---")