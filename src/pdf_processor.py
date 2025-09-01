import pdfplumber

def extract_text_from_pdf(file_path: str) -> dict | str:
    """Extracts all text from a PDF file."""
    print(f"Reading text from PDF file: {file_path}...")
    try:
        full_text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n\n"
        return full_text
    except Exception as e:
        return {"error": f"An error occurred while reading the PDF: {e}"}