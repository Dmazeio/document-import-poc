import json
from datetime import datetime
from openai import OpenAI

# --- HJELPEFUNKSJONER (brukes kun av AI-logikken) ---

def is_valid_iso_datetime(dt_string: str) -> bool:
    """Sjekker om en streng er et gyldig ISO 8601-tidsstempel."""
    if not isinstance(dt_string, str):
        return False
    try:
        # Bruker fromisoformat som er bygget for dette
        datetime.fromisoformat(dt_string)
        return True
    except ValueError:
        return False

# --- KJERNEFUNKSJONER (alt som har med AI og schema å gjøre) ---

def load_and_prepare_schema(schema_path: str) -> dict:
    """Laster en JSON-schemafil og forbereder den for bruk med OpenAI."""
    print(f"Laster og forbereder schema fra: {schema_path}...")
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)

        prepared_schema = {
            "fields": schema.get("fields", []),
            "expected_keys": [field["fieldname"] for field in schema.get("fields", [])],
            "datetime_fields": [field["fieldname"] for field in schema.get("fields", []) if field["type"] == "datetime"]
        }

        field_descriptions = []
        for i, field in enumerate(prepared_schema["fields"]):
            desc = f"{i+1}. '{field['fieldname']}': {field.get('description', 'Ingen beskrivelse.')}"
            if field['type'] == 'datetime':
                desc += " Denne MÅ formateres som en ISO 8601-streng (YYYY-MM-DDTHH:MM:SSZ)." # Bruk Z for UTC
            field_descriptions.append(desc)
        
        prepared_schema["field_instructions"] = "\n    ".join(field_descriptions)
        return prepared_schema
        
    except Exception as e:
        return {"error": f"En uventet feil oppstod under lasting av schema: {e}"}

def extract_data_based_on_schema(client: OpenAI, text_content: str, schema_info: dict) -> dict:
    """Sender tekst til OpenAI og ber om strukturert JSON basert på et dynamisk schema."""
    system_instruction = f"""
    Du er en ekspert på å analysere dokumenter og strukturere data i henhold til et strengt schema.
    Analyser brukerens tekst og trekk ut data for følgende felt:
    {schema_info['field_instructions']}

    VIKTIGE REGLER:
    - Svaret MÅ være et gyldig JSON-objekt.
    - JSON-objektet MÅ KUN inneholde nøklene: {json.dumps(schema_info['expected_keys'])}.
    - Hvis en verdi for et felt ikke finnes, returner `null`.

    Svar KUN med selve JSON-objektet.
    """

    try:
        print("Sender tekst til OpenAI for analyse basert på schema...")
        response = client.chat.completions.create(
            model="gpt-4o", # gpt-4o er et bra valg her
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": text_content}
            ]
        )
        data = json.loads(response.choices[0].message.content)
        
        # Validering av nøkler
        if sorted(data.keys()) != sorted(schema_info['expected_keys']):
            return {"error": f"Responsen fulgte ikke schema. Forventet: {schema_info['expected_keys']}, Mottok: {list(data.keys())}"}
        
        # Validering av dato-tidsformat
        for field_name in schema_info['datetime_fields']:
            dt_value = data.get(field_name)
            if dt_value is not None and not is_valid_iso_datetime(dt_value):
                return {"error": f"Verdien for '{field_name}' ('{dt_value}') er ikke i korrekt ISO 8601-format."}

        return data

    except Exception as e:
        return {"error": f"En feil oppstod under kallet til OpenAI: {e}"}