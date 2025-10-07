# ETTER (denne koden skal du lime inn)

import io  # VIKTIG: Importer io-biblioteket
import mammoth # Eller det biblioteket du bruker

def convert_file_to_markdown(document_bytes: bytes, filename: str) -> str:
    """
    Konverterer in-memory bytes av et .docx-dokument til markdown.

    Args:
        document_bytes: Rå bytes av .docx-filen.
        filename: Det originale filnavnet (brukes ikke her, men er god praksis å ha med).
    
    Returns:
        En string med markdown-innhold.
    """
    # Steg 1: Fjern `with open(...)` blokken.
    # Steg 2: Lag et "fil-lignende objekt" i minnet fra bytes.
    document_stream = io.BytesIO(document_bytes)

    # Steg 3: Send dette minne-objektet til konverteringsbiblioteket.
    # Koden herfra er sannsynligvis identisk med den du hadde før.
    result = mammoth.convert_to_markdown(document_stream)
    markdown_text = result.value
    
    # Kan være mer logikk her...
    return markdown_text