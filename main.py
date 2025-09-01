# main.py

import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. Last inn miljøvariabler fra .env-filen
load_dotenv()

# 2. Hent API-nøkkelen og initialiser OpenAI-klienten
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Finner ikke OPENAI_API_KEY. Sjekk din .env-fil.")

client = OpenAI(api_key=api_key)


# 3. Lag en funksjon for å stille et spørsmål
def still_spørsmål_til_openai(spørsmål):
    """Sender et spørsmål til OpenAI og returnerer svaret."""
    try:
        print("\nSender forespørsel til OpenAI...")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Du er en hjelpsom assistent."},
                {"role": "user", "content": spørsmål}
            ]
        )
        
        svar = response.choices[0].message.content
        return svar

    except Exception as e:
        return f"En feil oppstod: {e}"

# --- Kjør koden ---
if __name__ == "__main__":
    # ENDRING HER: Bruk input() for å hente spørsmål fra brukeren i terminalen
    mitt_spørsmål = input("Skriv inn ditt spørsmål og trykk Enter: ")
    
    # Resten er som før
    if mitt_spørsmål:
        svar_fra_openai = still_spørsmål_til_openai(mitt_spørsmål)
        
        print("\n--- Svar fra OpenAI ---")
        print(svar_fra_openai)
        print("------------------------")
    else:
        print("Du skrev ikke inn et spørsmål.")