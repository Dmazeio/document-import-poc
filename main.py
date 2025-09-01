import os
import json
import pdfplumber
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

# --- KONFIGURASJON ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Kunne ikke finne OPENAI_API_KEY. Sjekk din .env-fil.")
client = OpenAI(api_key=api_key)


# --- HJELPEFUNKSJONER ---

def is_valid_iso_datetime(dt_string):
    """Sjekker om en streng er et gyldig ISO 8601-tidsstempel med tidssone."""
    if not isinstance(dt_string, str):
        return False
    try:
        datetime.fromisoformat(dt_string)
        return True
    except ValueError:
        return False

def extract_text_from_pdf(file_path):
    """Trekker ut all tekst fra en PDF-fil."""
    print(f"Leser tekst fra PDF-fil: {file_path}...")
    try:
        full_text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n\n"
        return full_text
    except FileNotFoundError:
        return {"error": f"Filen ble ikke funnet på stien: {file_path}"}
    except Exception as e:
        return {"error": f"En feil oppstod under lesing av PDF-en: {e}"}

# --- KJERNEFUNKSJONER ---

def load_and_prepare_schema(schema_path):
    """
    Laster en JSON-schemafil og forbereder den for bruk med OpenAI.
    Returnerer en dictionary med all nødvendig info for prompt og validering.
    """
    print(f"Laster og forbereder schema fra: {schema_path}...")
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)

        prepared_schema = {
            "fields": schema.get("fields", []),
            "expected_keys": [field["fieldname"] for field in schema.get("fields", [])],
            "datetime_fields": [field["fieldname"] for field in schema.get("fields", []) if field["type"] == "datetime"]
        }

        # Bygg en detaljert beskrivelse for AI-en basert på schema
        field_descriptions = []
        for i, field in enumerate(prepared_schema["fields"]):
            desc = f"{i+1}. '{field['fieldname']}': {field.get('description', 'Ingen beskrivelse.')}"
            if field['type'] == 'datetime':
                desc += " Denne MÅ formateres som en ISO 8601-streng (YYYY-MM-DDTHH:MM:SS±hh:mm)."
            field_descriptions.append(desc)
        
        prepared_schema["field_instructions"] = "\n    ".join(field_descriptions)
        return prepared_schema
        
    except FileNotFoundError:
        return {"error": f"Schema-filen ble ikke funnet på stien: {schema_path}"}
    except json.JSONDecodeError:
        return {"error": f"Kunne ikke parse JSON fra schema-filen: {schema_path}"}
    except Exception as e:
        return {"error": f"En uventet feil oppstod under lasting av schema: {e}"}

def extract_data_based_on_schema(text_content, schema_info):
    """
    Sender tekst til OpenAI og ber om strukturert JSON basert på et dynamisk schema.
    """
    system_instruction = f"""
    Du er en ekspert på å analysere dokumenter og strukturere data i henhold til et strengt schema.
    Analyser brukerens tekst og trekk ut data for følgende felt:
    {schema_info['field_instructions']}

    VIKTIGE REGLER FOR FORMATERING:
    - Svaret MÅ være et gyldig JSON-objekt.
    - JSON-objektet MÅ KUN inneholde nøklene: {json.dumps(schema_info['expected_keys'])}.
    - Hvis en verdi for et felt ikke finnes i teksten, MÅ du returnere `null` for det feltet. Ikke gjett.
    
    Svar KUN med selve JSON-objektet.
    """

    try:
        print("Sender tekst til OpenAI for analyse basert på schema...")
        response = client.chat.completions.create(
            model="gpt-5o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": text_content}
            ]
        )
        json_response_str = response.choices[0].message.content
        data = json.loads(json_response_str)
        
        # --- STRENG VALIDERING MOT SCHEMA ---
        # 1. Validering av nøkler
        if sorted(data.keys()) != sorted(schema_info['expected_keys']):
            return {"error": f"Responsen fulgte ikke schema. Forventet nøkler: {schema_info['expected_keys']}, Mottok: {list(data.keys())}"}
        
        # 2. Validering av dato-tidsformat
        for field_name in schema_info['datetime_fields']:
            dt_value = data.get(field_name)
            if dt_value is not None and not is_valid_iso_datetime(dt_value):
                return {"error": f"Verdien for '{field_name}' ('{dt_value}') er ikke i korrekt ISO 8601-format."}

        # --- Post-prosessering (som før, men med dynamiske feltnavn) ---
        start_field = 'startuptime'
        end_field = 'endtime'
        if start_field in data and end_field in data:
            start_dt = data.get(start_field)
            end_dt = data.get(end_field)
            if start_dt and not end_dt:
                data[end_field] = start_dt
                print(f"Info: '{end_field}' ikke funnet. Setter den lik '{start_field}'.")
            elif end_dt and not start_dt:
                data[start_field] = end_dt
                print(f"Info: '{start_field}' ikke funnet. Setter den lik '{end_field}'.")
            
        return data

    except json.JSONDecodeError:
        return {"error": "Klarte ikke å dekode JSON-responsen fra OpenAI."}
    except Exception as e:
        return {"error": f"En feil oppstod under kallet til OpenAI: {e}"}


# --- HOVEDLOGIKK ---
if __name__ == "__main__":
    pdf_file_path = "Minutes_of_meeting_samples/SampleMinutes-1.pdf"
    schema_file_path = "meeting_template.json" # Stien til ditt schema
    
    # 1. Last inn og forbered schema
    schema_info = load_and_prepare_schema(schema_file_path)
    if "error" in schema_info:
        print(f"KRITISK FEIL: {schema_info['error']}")
    else:
        # 2. Trekk ut tekst fra PDF
        raw_text_from_pdf = extract_text_from_pdf(pdf_file_path)
        
        if "error" in raw_text_from_pdf:
            print(f"Feil: {raw_text_from_pdf['error']}")
        else:
            print("Tekst ble trukket ut fra PDF.")
            
            # 3. Trekk ut strukturert data basert på schema
            structured_data = extract_data_based_on_schema(raw_text_from_pdf, schema_info)
            
            print("\n--- Resultat fra OpenAI (validert mot schema) ---")
            print(json.dumps(structured_data, indent=2, ensure_ascii=False))
            print("-------------------------------------------------")