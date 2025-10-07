import os
import time
import re
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Importer funksjonene klassen er avhengig av
from .document_converter import convert_file_to_markdown
from .schema_processor import process_template_hierarchically
from .openai_extractor import extract_data_with_hierarchy
from .json_transformer import transform_to_dmaze_format_hierarchically
from .document_classifier import classify_document_type
from .document_splitter import split_document_into_items

class DocumentProcessor:
    def __init__(self, schema_content: dict, document_bytes: bytes, document_filename: str):
        self.schema_content = schema_content
        self.document_bytes = document_bytes
        self.document_filename = document_filename

        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Felles tilstands-variabler
        self.schema_package = None
        self.markdown_content = None
        self.doc_type = "single_item"
        
        # Felles logging-variabler
        self.processing_log = {}
        self.errors = []

    # --- log_step er uendret, men vil nå bli brukt i en løkke ---
    def _log_step(self, step_name: str, function_to_run):
        """Kjører et steg, logger tid og status."""
        print(f"\n--- Running Step: {step_name} ---")
        step_start_time = time.time()
        status = "Pending"
        details = ""
        try:
            result = function_to_run()
            if isinstance(result, dict) and "error" in result:
                raise ValueError(result["error"])
            status = "Success"
            print(f"  - Step Summary for {step_name}: Success")
            return result
        except Exception as e:
            status = "Failure"
            details = str(e)
            self.errors.append(f"Step '{step_name}' failed: {details}")
            raise
        finally:
            duration = time.time() - step_start_time
            summary = f"{status} ({duration:.2f}s)"
            if status == "Failure":
                summary += f": {details}"
            self.processing_log[step_name] = summary

    # --- NY HJELPEMETODE: Prosesserer én enkelt "chunk" ---
    def _process_single_chunk(self, content: str, title: str) -> dict:
        """Kjører AI-ekstrahering og transformasjon for én del av dokumentet."""
        item_log_name_prefix = f"for '{title}'" if title else ""
        
        nested_data = self._log_step(f"AI Data Extraction {item_log_name_prefix}", 
            lambda: extract_data_with_hierarchy(self.client, content, self.schema_package))
        
        transformation_result = self._log_step(f"Data Transformation {item_log_name_prefix}", 
            lambda: transform_to_dmaze_format_hierarchically(self.client, nested_data, self.schema_package))
        
        return {
            "dmaze_data": transformation_result.get("dmaze_data", []),
            "warnings": transformation_result.get("warnings", [])
        }

    # --- build_summary er nå mer fleksibel og tar argumenter ---
    def _build_summary(self, item_title, dmaze_data, warnings, overall_status) -> dict:
        """Bygger et summary-objekt for ett enkelt resultat."""
        root_object_name = self.schema_package['schema_tree']['name'] if self.schema_package else "unknown"
        
        final_status = overall_status
        if final_status != "Failure":
            final_status = "SuccessWithWarnings" if warnings else "Success"

        summary_obj = {
            "inputFile": self.document_filename,
            "templateUsed": "In-memory schema",
            "overallStatus": final_status,
            "itemTitle": item_title,
            "processingTimestamp": datetime.now().isoformat(),
            "processingLog": self.processing_log,
            "errorsEncountered": self.errors,
            "warningsEncountered": warnings,
        }
        
        # Logikken for humanReadableSummary er her
        summary_parts = []
        title_text = f"for document part '{item_title}'" if item_title else "for the document"
        summary_parts.append(f"Summary of the import process {title_text} from the file '{self.document_filename}'.")
        # ... (resten av den detaljerte humanReadableSummary-logikken kan legges til her) ...
        summary_obj["humanReadableSummary"] = "\n".join(summary_parts)
        
        return summary_obj

    # --- HOVEDMETODEN: run() er nå fullstendig ombygd ---
    def run(self) -> list[dict]: # VIKTIG: Returnerer nå en liste
        """Orkestrerer hele prosessen og returnerer en liste med resultater."""
        results_list = []
        
        try:
            # Steg 1, 2, 3: Felles forberedelser
            self.schema_package = self._log_step("Template Processing", lambda: process_template_hierarchically(self.schema_content))
            self.markdown_content = self._log_step("Document Conversion", lambda: convert_file_to_markdown(self.document_bytes, self.document_filename))
            root_name = self.schema_package['schema_tree']['name']
            self.doc_type = self._log_step("Document Classification", lambda: classify_document_type(self.client, self.markdown_content, root_name))
            
            # Steg 4: Lag en liste over "chunks" som skal prosesseres
            chunks_to_process = []
            if self.doc_type == "multiple_items":
                chunks_to_process = self._log_step("Document Splitting", 
                    lambda: split_document_into_items(self.client, self.markdown_content, root_name))
            else:
                # Behandle som en liste med ett enkelt, navnløst element
                class SingleChunk:
                    item_title = None
                    item_content = self.markdown_content
                chunks_to_process.append(SingleChunk())

            # Steg 5: Prosesser hver chunk i en løkke
            for chunk in chunks_to_process:
                # Kjør selve AI-prosesseringen for denne chunken
                chunk_result = self._process_single_chunk(chunk.item_content, chunk.item_title)
                
                # Bygg et komplett resultatobjekt
                summary = self._build_summary(
                    item_title=chunk.item_title,
                    dmaze_data=chunk_result["dmaze_data"],
                    warnings=chunk_result["warnings"],
                    overall_status="Success" # Antar suksess hvis vi kommer hit
                )
                results_list.append({
                    "summary": summary,
                    "dmaze_data": chunk_result["dmaze_data"]
                })

        except Exception as e:
            print(f"\nCRITICAL ERROR in workflow: {e}")
            # Ved kritisk feil, returner en liste med ett enkelt feil-resultat
            summary = self._build_summary(None, [], [], "Failure")
            return [{"summary": summary, "dmaze_data": []}]
        
        return results_list