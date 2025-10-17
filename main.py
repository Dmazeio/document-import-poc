import os
import json
import re

from src.document_processor import DocumentProcessor

def sanitize_filename(name: str) -> str:
    """Sanitize a string so it is a valid file name."""
    if not name:
        return ""
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    return name[:100].strip()

if __name__ == "__main__":
    # --- Part 1: Define input files ---
    input_doc_path = "input_documents/ROS-Analyse_Stange_kommune_2023-2027__word.docx"
    template_path = "input-schemas/Risk Assessment - Enterprise Risk Assessment.json"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    print("--- Running in CLI test mode ---")

    # --- Part 2: Read files into memory ---
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            schema_data = json.load(f)
        with open(input_doc_path, 'rb') as f:
            doc_bytes = f.read()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        exit()

    # --- Part 3: Create and run the processor ---
    print(f"Processing document '{input_doc_path}'...")
    processor = DocumentProcessor(
        schema_content=schema_data,
        document_bytes=doc_bytes,
        document_filename=os.path.basename(input_doc_path)
    )
    results = processor.run()  # Now receives a LIST of results

    # --- Part 4: Handle and save results ---
    print(f"\n--- Processing returned {len(results)} result(s). Saving to output folder... ---")
    
    for i, result in enumerate(results):
        summary = result.get("summary", {})
        item_title = summary.get("itemTitle")
        
        # Build a unique and safe filename
        base_name = sanitize_filename(item_title) if item_title else os.path.splitext(os.path.basename(input_doc_path))[0]
        # Add a counter if there are multiple results or no title
        if len(results) > 1 and not item_title:
             output_filename = f"{base_name}_item_{i+1}_dmaze_import.json"
        elif len(results) > 1:
            output_filename = f"{base_name}_{i+1}_dmaze_import.json"
        else:
            output_filename = f"{base_name}_dmaze_import.json"

        output_path = os.path.join(output_dir, output_filename)
        
        print(f"  - Saving result to '{output_path}'")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

    print("\n--- Processing is complete. ---")