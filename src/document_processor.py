import os
import time
import re
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

from .ai_client import AIClient

# Import functions this class depends on
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
        # Create an instance of the general AIClient
        self.ai_client = AIClient(OpenAI(api_key=os.getenv("OPENAI_API_KEY")))

        self.schema_package = None
        self.markdown_content = None
        self.doc_type = "single_item"

        # Common logging variables
        self.processing_log = {}
        self.errors = []

    def _log_step(self, step_name: str, function_to_run):
        """Run a processing step, log duration and status."""
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

    def _process_single_chunk(self, content: str, title: str) -> dict:
        """Run AI extraction and transformation for one part of the document."""
        item_log_name_prefix = f"for '{title}'" if title else ""
        
        nested_data = self._log_step(f"AI Data Extraction {item_log_name_prefix}", 
            lambda: extract_data_with_hierarchy(self.ai_client, content, self.schema_package))
        
        transformation_result = self._log_step(f"Data Transformation {item_log_name_prefix}", 
            lambda: transform_to_dmaze_format_hierarchically(self.ai_client, nested_data, self.schema_package))
        
        return {
            "dmaze_data": transformation_result.get("dmaze_data", []),
            "warnings": transformation_result.get("warnings", [])
        }


    def _build_summary(self, item_title, dmaze_data, warnings, overall_status, total_num_chunks: int, item_processing_duration: float) -> dict:
        """Builds a summary object for a single result."""
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
        
        summary_parts = []
        title_text = f"for document part '{item_title}'" if item_title else "for the document"
        
        summary_parts.append(f"Summary of the import process {title_text} from the file '{self.document_filename}'.")
        
        summary_parts.append(f"  - Total parts identified in document: {total_num_chunks}.")
        summary_parts.append(f"  - Status for this part: {final_status} (processed in {item_processing_duration:.2f} seconds).")
        
        num_errors = len(self.errors)
        num_warnings = len(warnings)
        summary_parts.append(f"  - Errors encountered for this part: {num_errors}.")
        if num_errors > 0:
            summary_parts.append(f"    Details: {'; '.join(self.errors)}")
        
        summary_parts.append(f"  - Warnings encountered for this part: {num_warnings}.")
        if num_warnings > 0:
            # Limit the number of warnings shown directly in the human-readable summary for readability
            displayed_warnings = warnings[:3]  # Show the first 3 warnings
            remaining_warnings = num_warnings - len(displayed_warnings)

            summary_parts.append(f"    Important warnings: {'; '.join(displayed_warnings)}")
            if remaining_warnings > 0:
                summary_parts.append(f"    ({remaining_warnings} more warnings not listed here. See 'warningsEncountered' for full list.)")
        
        summary_obj["humanReadableSummary"] = "\n".join(summary_parts)
        
        return summary_obj

    # Note: run() returns a list of results
    def run(self) -> list[dict]:
        """Orchestrates the full processing pipeline and returns a list of results."""
        results_list = []
        
        try:
            # Steps 1-3: Common preparations
            self.schema_package = self._log_step("Template Processing", lambda: process_template_hierarchically(self.schema_content))
            self.markdown_content = self._log_step("Document Conversion", lambda: convert_file_to_markdown(self.document_bytes, self.document_filename))
            root_name = self.schema_package['schema_tree']['name']
            
            # Pass the ai_client instance
            self.doc_type = self._log_step("Document Classification", lambda: classify_document_type(self.ai_client, self.markdown_content, root_name))
            
            # Step 4: Build a list of chunks to process
            chunks_to_process = []
            if self.doc_type == "multiple_items":
                # Pass the ai_client instance
                chunks_to_process = self._log_step("Document Splitting", 
                    lambda: split_document_into_items(self.ai_client, self.markdown_content, root_name))
            else:
                class SingleChunk:
                    item_title = None
                    item_content = self.markdown_content
                chunks_to_process.append(SingleChunk())

            total_num_chunks = len(chunks_to_process)

            # Step 5: Process each chunk individually
            for chunk in chunks_to_process:
                item_start_time = time.time()
                chunk_result = self._process_single_chunk(chunk.item_content, chunk.item_title)
                item_processing_duration = time.time() - item_start_time

                summary = self._build_summary(
                    item_title=chunk.item_title,
                    dmaze_data=chunk_result["dmaze_data"],
                    warnings=chunk_result["warnings"],
                    overall_status="Success",
                    total_num_chunks=total_num_chunks,
                    item_processing_duration=item_processing_duration
                )
                results_list.append({
                    "summary": summary,
                    "dmaze_data": chunk_result["dmaze_data"]
                })

        except Exception as e:
            print(f"\nCRITICAL ERROR in workflow: {e}")
            summary = self._build_summary(None, [], [], "Failure", total_num_chunks=0, item_processing_duration=0.0)
            return [{"summary": summary, "dmaze_data": []}]
        
        return results_list