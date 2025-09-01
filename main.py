import os
import json
import pdfplumber
from openai import OpenAI
from dotenv import load_dotenv

# --- KONFIGURASJON ---
# 1. Last inn miljøvariabler fra .env-filen
load_dotenv()

# 2. Hent API-nøkkel og initialiser OpenAI-klienten
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Kunne ikke finne OPENAI_API_KEY. Sjekk din .env-fil.")
client = OpenAI(api_key=api_key)


# --- FUNKSJONER ---

def extract_text_from_pdf(file_path):
    """
    Åpner en PDF-fil og trekker ut all tekst fra alle sider.
    Returnerer teksten som en enkelt streng.
    """
    print(f"Leser tekst fra PDF-fil: {file_path}...")
    try:
        full_text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n\n"  # Legg til linjeskift mellom sider
        return full_text
    except FileNotFoundError:
        return {"error": f"Filen ble ikke funnet på stien: {file_path}"}
    except Exception as e:
        return {"error": f"En feil oppstod under lesing av PDF-en: {e}"}

def extract_meeting_data_as_json(meeting_text):
    """
    Sender ustrukturert møtetekst til OpenAI og ber om strukturert JSON i retur.
    Validerer at responsen kun inneholder de forventede feltene.
    """
    # Definer malen og de forventede nøklene
    expected_keys = ["title", "description", "date"]
    data_template = {
        "title": "...",
        "description": "...",
        "date": "YYYY-MM-DD"
    }
    
    # Definer en detaljert og streng instruksjon for modellen
    system_instruction = f"""
    Du er en ekspert på å analysere møtereferater.
    Analyser brukerens tekst. Trekk ut følgende datafelt:
    1.  'title': Hovedtittelen til møtet.
    2.  'description': En kort oppsummering av møtets formål.
    3.  'date': Datoen for møtet.

    Formater responsen din som et gyldig JSON-objekt.
    JSON-objektet MÅ KUN inneholde følgende nøkler: {json.dumps(expected_keys)}.
    Ikke legg til, fjern eller endre navn på noen av nøklene.
    Strukturen SKAL være nøyaktig som denne malen:
    {json.dumps(data_template, indent=4)}
    
    Svar KUN med selve JSON-objektet, uten ekstra tekst eller forklaringer.
    """

    try:
        print("Sender tekst til OpenAI for analyse...")
        response = client.chat.completions.create(
            model="gpt-4o",  # Anbefaler gpt-4o for bedre instruksjonsfølging
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": meeting_text}
            ]
        )
        json_response_str = response.choices[0].message.content
        
        # Validering av responsen
        data = json.loads(json_response_str)
        
        # Sjekk at kun de forventede nøklene finnes
        if not isinstance(data, dict) or sorted(data.keys()) != sorted(expected_keys):
            return {"error": f"OpenAI-responsen fulgte ikke det forventede formatet. Mottok nøkler: {list(data.keys())}"}
            
        return data

    except json.JSONDecodeError:
        return {"error": "Klarte ikke å dekode JSON-responsen fra OpenAI."}
    except Exception as e:
        return {"error": f"En feil oppstod under kallet til OpenAI: {e}"}


# --- HOVEDLOGIKK ---
if __name__ == "__main__":
    # Definer stien til PDF-filen du vil analysere
    pdf_file_path = "Minutes_of_meeting_samples/SampleMinutes-1.pdf"
    
    # Steg 1: Trekk ut tekst fra PDF
    raw_text_from_pdf = extract_text_from_pdf(pdf_file_path)
    
    # Sjekk om tekstutvinning var vellykket
    if isinstance(raw_text_from_pdf, dict) and "error" in raw_text_from_pdf:
        print(f"Feil: {raw_text_from_pdf['error']}")
    else:
        print("Tekst ble trukket ut fra PDF.")
        
        # Steg 2: Send teksten til OpenAI for å få strukturerte data
        structured_data = extract_meeting_data_as_json(raw_text_from_pdf)
        
        print("\n--- Resultat fra OpenAI ---")
        # Bruk json.dumps for å "pen-printe" resultatet med innrykk
        print(json.dumps(structured_data, indent=2, ensure_ascii=False))
        print("--------------------------")