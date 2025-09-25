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

# --- KONFIGURASJON ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Could not find OPENAI_API_KEY. Check your .env file.")
client = OpenAI(api_key=api_key)


def log_step(processing_log: dict, step_name: str, function_to_run, errors_list: list):
    """
    Kjører en funksjon, printer detaljer til konsollen, og legger til
    en kompakt en-linjes oppsummering i 'processing_log'-ordboken.
    Samler også opp feilmeldinger i errors_list.
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
        errors_list.append(f"Steg '{step_name}' feilet: {details}")
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
    Genererer en menneskevennlig oppsummering av importprosessen for et gitt element eller dokument.
    """
    overall_status = summary_obj.get("overallStatus", "Ukjent status")
    input_file_basename = os.path.basename(summary_obj.get("inputFile", "ukjent fil"))
    template_basename = os.path.basename(summary_obj.get("templateUsed", "ukjent mal"))
    item_title = summary_obj.get("itemTitle")
    errors = summary_obj.get("errorsEncountered", [])
    
    summary_parts = []

    # Innledende utsagn om behandlingen
    if item_title:
        summary_parts.append(f"Oppsummering av importprosessen for dokumentdel '{item_title}' fra filen '{input_file_basename}', basert på malen '{template_basename}'.")
    else:
        summary_parts.append(f"Oppsummering av importprosessen for dokumentet '{input_file_basename}', basert på malen '{template_basename}'.")

    # Overordnet status og hva som ble generert
    if overall_status == "Success":
        summary_parts.append("\n**Overordnet status:** ✅ Vellykket")
        if dmaze_data:
            num_dmaze_objects = len(dmaze_data)
            num_root_objects = sum(1 for obj in dmaze_data if obj.get('objectname') == root_object_name)
            
            if num_root_objects > 0:
                summary_parts.append(f"Det ble generert totalt {num_dmaze_objects} Dmaze-objekter, hvorav {num_root_objects} er hovedobjekter av typen '{root_object_name}'.")
            else:
                summary_parts.append(f"Prosessen genererte {num_dmaze_objects} Dmaze-objekter, men ingen av dem er av hovedtypen '{root_object_name}'. Dette kan indikere et problem med skjema eller ekstraksjon.")
        else:
            summary_parts.append("Ingen Dmaze-objekter ble generert, selv om den tekniske prosessen indikerer suksess. Dette kan skyldes manglende data i dokumentet eller et problem med dataekstraksjon.")
    else: # overall_status is Failure
        summary_parts.append("\n**Overordnet status:** ❌ Mislykket")
        if dmaze_data:
             summary_parts.append(f"Prosessen genererte {len(dmaze_data)} Dmaze-objekter før den feilet. Se 'Feil som oppstod' for mer informasjon.")
        else:
            summary_parts.append("Ingen Dmaze-objekter ble generert på grunn av feil i prosessen.")

    # Hva som gikk bra og hva som ikke gikk bra
    successful_steps = [step for step, status in summary_obj.get("processingLog", {}).items() if "Success" in status]
    failed_steps = [step for step, status in summary_obj.get("processingLog", {}).items() if "Failure" in status]

    if successful_steps:
        summary_parts.append(f"\n**Vellykkede steg:** {', '.join(successful_steps)}.")
    if failed_steps:
        summary_parts.append(f"**Steg som feilet:** {', '.join(failed_steps)}. Se 'Feil som oppstod' for detaljer.")

    # Liste spesifikke feil
    if errors:
        summary_parts.append("\n**Feil som oppstod:**")
        for error_msg in errors:
            summary_parts.append(f"- {error_msg}")
    else:
        summary_parts.append("\nIngen spesifikke feil ble registrert under behandlingen.")

    return "\n".join(summary_parts)


# --- HOVEDLOGIKKEN I PROGRAMMET ---
if __name__ == "__main__":
    input_file_path = "input_documents/sample_4.docx"
    template_file_path = "input-schemas/Minutes of Meeting.json"
    
    os.makedirs("output", exist_ok=True)

    # Initialiser global feilliste for hele kjøringen
    all_errors_during_run = []
    root_object_name_global = "ukjent" # Fallback hvis skjemabehandling feiler

    try:
        initial_log = {} 
        
        schema_package = log_step(initial_log, "Template Processing", 
                                  lambda: process_template_hierarchically(template_file_path), all_errors_during_run)
        root_object_name_global = schema_package['schema_tree']['name']

        markdown_content = log_step(initial_log, "Document Conversion", 
                                    lambda: convert_file_to_markdown(input_file_path), all_errors_during_run)

        doc_type = log_step(initial_log, "Document Classification", 
                            lambda: classify_document_type(client, markdown_content, root_object_name_global), all_errors_during_run)
        
        if doc_type == "multiple_items":
            item_chunks = log_step(initial_log, "Document Splitting", 
                                   lambda: split_document_into_items(client, markdown_content, root_object_name_global), all_errors_during_run)
            
            print(f"\n--- Fant {len(item_chunks)} elementer. Behandler og lagrer hver enkelt individuelt. ---")
            
            for i, chunk in enumerate(item_chunks):
                print(f"\n{'='*20} BEHANDLER ELEMENT {i+1}/{len(item_chunks)}: '{chunk.item_title}' {'='*20}")
                
                # Hvert element starter med en kopi av globale feil og sin egen logg
                item_log = initial_log.copy()
                item_errors = all_errors_during_run.copy() 
                
                item_summary = {
                    "inputFile": input_file_path, "templateUsed": template_file_path,
                    "overallStatus": "Pending", "itemTitle": chunk.item_title,
                    "processingTimestamp": datetime.now().isoformat(),
                    "processingLog": item_log,
                    "errorsEncountered": item_errors 
                }
                item_final_data = []

                try:
                    nested_data = log_step(item_log, "AI Data Extraction", 
                                           lambda: extract_data_with_hierarchy(client, chunk.item_content, schema_package), item_errors)
                    
                    item_final_data = log_step(item_log, "Data Transformation", 
                                               lambda: transform_to_dmaze_format_hierarchically(client, nested_data, schema_package), item_errors)
                    item_summary["overallStatus"] = "Success"
                except Exception: # Feil er allerede logget i log_step, oppdaterer kun overallStatus her
                    item_summary["overallStatus"] = "Failure"
                finally:
                    # errorsEncountered er allerede oppdatert av log_step
                    item_summary["humanReadableSummary"] = generate_human_readable_summary(item_summary, root_object_name_global, item_final_data)

                    final_output = {"summary": item_summary, "dmaze_data": item_final_data}
                    # Sikrer at filnavnet er trygt
                    safe_title = "".join(x for x in chunk.item_title if x.isalnum() or x in [' ', '-']).replace(' ', '_')[:50]
                    if not safe_title: # Fallback hvis tittelen blir tom etter rensing
                        safe_title = f"item_{i+1}"
                    item_output_path = f"output/{safe_title}_dmaze_import.json"
                    
                    print(f"\n--- Skriver endelig logg for '{chunk.item_title}' til {item_output_path} ---")
                    with open(item_output_path, "w", encoding="utf-8") as f:
                        json.dump(final_output, f, indent=4, ensure_ascii=False)

        else: # single_item
            summary_log = {
                "inputFile": input_file_path, "templateUsed": template_file_path,
                "overallStatus": "Pending", "processingTimestamp": datetime.now().isoformat(),
                "processingLog": initial_log,
                "errorsEncountered": all_errors_during_run # Inneholder feil fra initielle steg
            }
            final_flat_data = []

            try:
                nested_data = log_step(initial_log, "AI Data Extraction", 
                                       lambda: extract_data_with_hierarchy(client, markdown_content, schema_package), all_errors_during_run)
                
                final_flat_data = log_step(initial_log, "Data Transformation", 
                                           lambda: transform_to_dmaze_format_hierarchically(client, nested_data, schema_package), all_errors_during_run)
                summary_log["overallStatus"] = "Success"
            except Exception: # Feil er allerede logget i log_step, oppdaterer kun overallStatus her
                summary_log["overallStatus"] = "Failure"
            finally:
                # errorsEncountered er allerede oppdatert av log_step
                summary_log["humanReadableSummary"] = generate_human_readable_summary(summary_log, root_object_name_global, final_flat_data)

                final_output = {"summary": summary_log, "dmaze_data": final_flat_data}
                output_filename = os.path.splitext(os.path.basename(input_file_path))[0]
                output_file_path = f"output/{output_filename}_dmaze_import.json"
                print(f"\n--- Skriver endelig logg til {output_file_path} ---")
                with open(output_file_path, "w", encoding="utf-8") as f:
                    json.dump(final_output, f, indent=4, ensure_ascii=False)

    except Exception as e:
        # Denne fanger kritiske feil som forhindrer selv initial oppsett eller skjemabehandling
        print(f"\nKRITISK FEIL under initial oppsett eller hovedprosess. Feil: {e}")
        # Forsøk å lage en minimal oppsummeringslogg hvis mulig
        if 'summary_log' not in locals(): # Hvis summary_log ikke engang ble opprettet
            summary_log = {
                "inputFile": input_file_path, "templateUsed": template_file_path,
                "overallStatus": "Failure", "processingTimestamp": datetime.now().isoformat(),
                "processingLog": initial_log if 'initial_log' in locals() else {},
                "errorsEncountered": all_errors_during_run 
            }
        
        if not all_errors_during_run or not any("KRITISK FEIL" in err for err in all_errors_during_run):
            # Legg kun til hvis ikke allerede lagt til, eller hvis det er en ny kritisk feil
            all_errors_during_run.append(f"KRITISK FEIL: {e}")
        
        summary_log["overallStatus"] = "Failure"
        summary_log["errorsEncountered"] = all_errors_during_run
        summary_log["humanReadableSummary"] = generate_human_readable_summary(summary_log, root_object_name_global, []) # Tom dmaze_data for kritiske feil

        output_filename = os.path.splitext(os.path.basename(input_file_path))[0]
        output_file_path = f"output/{output_filename}_dmaze_import_KRITISK_FEIL.json" # Eget filnavn for kritiske feil
        print(f"\n--- Forsøker å skrive delvis logg for kritisk feil til {output_file_path} ---")
        try:
            with open(output_file_path, "w", encoding="utf-8") as f:
                json.dump({"summary": summary_log, "dmaze_data": []}, f, indent=4, ensure_ascii=False)
        except Exception as file_write_e:
            print(f"Klarte ikke å skrive kritisk feillogg: {file_write_e}")


    print("\n--- Behandlingen er ferdig. ---")