import os
import json
import re

# Importer kun den ene klassen vi trenger
from src.document_processor import DocumentProcessor

def sanitize_filename(name: str) -> str:
    """Renser en streng slik at den er et gyldig filnavn."""
    if not name:
        return ""
    # Fjern ugyldige tegn
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Begrens lengden
    return name[:100].strip()

if __name__ == "__main__":
    # --- Del 1: Definer input-filer ---
    input_doc_path = "input_documents/sample_4.docx"
    template_path = "input-schemas/Minutes of Meeting.json"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    print("--- Running in CLI test mode ---")

    # --- Del 2: Les filer inn i minnet ---
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            schema_data = json.load(f)
        with open(input_doc_path, 'rb') as f:
            doc_bytes = f.read()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        exit()

    # --- Del 3: Opprett og kjør prosessoren ---
    print(f"Processing document '{input_doc_path}'...")
    processor = DocumentProcessor(
        schema_content=schema_data,
        document_bytes=doc_bytes,
        document_filename=os.path.basename(input_doc_path)
    )
    results = processor.run() # Mottar nå en LISTE med resultater

    # --- Del 4: Håndter og lagre resultatene ---
    print(f"\n--- Processing returned {len(results)} result(s). Saving to output folder... ---")
    
    for i, result in enumerate(results):
        summary = result.get("summary", {})
        item_title = summary.get("itemTitle")
        
        # Lag et unikt og trygt filnavn
        base_name = sanitize_filename(item_title) if item_title else os.path.splitext(os.path.basename(input_doc_path))[0]
        # Legg til en teller hvis det er flere med samme navn eller ingen tittel
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