# File: check_api.py
# En oppdatert testfil for å fange og printe ut fulle API-respons-headers.

import os
from openai import OpenAI, APIStatusError ### ENDRING: Importer den spesifikke feilklassen
from dotenv import load_dotenv

# 1. Konfigurasjon
print("--- Laster API-nøkkel fra .env-fil... ---")
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("\nFEIL: Kunne ikke finne OPENAI_API_KEY. Sjekk at .env-filen din er korrekt.")
else:
    print("API-nøkkel funnet. Prøver å koble til OpenAI...")
    
    try:
        if not api_key.startswith("sk-svcacct-2n3S8A1") and not api_key.endswith("68510mYLQA"):
            print("Feil API nøkkel")
        # 2. Initialiser klienten
        client = OpenAI(api_key=api_key)

        # 3. Utfør et enkelt AI-kall
        print("\n--- Sender en enkel test-forespørsel til OpenAI... ---")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Si 'Hello, World!' på norsk."}
            ]
        )

        # 4. Skriv ut resultatet ved suksess
        ai_message = response.choices[0].message.content
        print("\n-----------------------------------------")
        print(" SUKSESS! Fikk svar fra OpenAI.")
        print(f"   Svar fra AI: '{ai_message}'")
        print("-----------------------------------------")

        print(response)

    ### ENDRING: Fang den spesifikke feilen for å få tilgang til respons-objektet ###
    except APIStatusError as e:
        print("\n-----------------------------------------")
        print(" FEIL: Et API-kall feilet med en statuskode.")
        print(f"   Statuskode: {e.status_code}")
        print(f"   Feilmelding (body): {e.response.text}")
        
        print("\n--- FULLE RESPONSE HEADERS ---")
        # Loop gjennom og print hver header på en egen linje for lesbarhet
        for key, value in e.response.headers.items():
            print(f"   {key}: {value}")
        print("-----------------------------------------")
        print(e)

    except Exception as e:
        # Fanger opp andre, generelle feil (f.eks. nettverksproblemer)
        print("\n-----------------------------------------")
        print(" EN ANNEN FEIL OPPSTOD:")
        print(f"   Feiltype: {type(e).__name__}")
        print(f"   Detaljer: {e}")
        print("-----------------------------------------")
