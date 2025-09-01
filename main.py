# main.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Importer funksjonene fra de nye filene dine!
from src.pdf_processor import extract_text_from_pdf
from src.openai_extractor import load_and_prepare_schema, extract_data_based_on_schema

# --- KONFIGURASJON ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Kunne ikke finne OPENAI_API_KEY. Sjekk din .env-fil.")
client = OpenAI(api_key=api_key)


# --- HOVEDLOGIKK ---
if __name__ == "__main__":
    pdf_file_path = "input_documents/SampleMinutes-1.pdf"
    schema_file_path = "meeting_template.json"
    
    # Steg 1: Last inn og forbered schema
    schema_info = load_and_prepare_schema(schema_file_path)
    if "error" in schema_info:
        print(f"KRITISK FEIL: {schema_info['error']}")
    else:
        # Steg 2: Trekk ut tekst fra PDF
        raw_text = extract_text_from_pdf(pdf_file_path)
        
        if isinstance(raw_text, dict) and "error" in raw_text:
            print(f"Feil: {raw_text['error']}")
        else:
            print("Tekst ble trukket ut fra PDF.")
            
            # Steg 3: Trekk ut strukturert data basert på schema
            structured_data = extract_data_based_on_schema(client, raw_text, schema_info)
            
            print("\n--- Resultat fra OpenAI (validert mot schema) ---")
            print(json.dumps(structured_data, indent=2, ensure_ascii=False))
            print("-------------------------------------------------")