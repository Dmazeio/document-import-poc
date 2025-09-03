# File: src/pdf_processor.py

from pypdf import PdfReader

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts all text from a PDF file and returns it as a single string.
    """
    try:
        reader = PdfReader(file_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
        return full_text
    except FileNotFoundError:
        return {"error": f"PDF file not found at: {file_path}"}
    except Exception as e:
        return {"error": f"An error occurred while reading the PDF: {e}"}