import pdfplumber

def extract_text_from_pdf(file_path: str) -> dict | str:
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
    except Exception as e:
        return {"error": f"En feil oppstod under lesing av PDF-en: {e}"}