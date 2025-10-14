import io
import mammoth


def convert_file_to_markdown(document_bytes: bytes, filename: str) -> str:
    """
    Convert in-memory bytes of a .docx document to Markdown.

    Args:
        document_bytes: Raw bytes of the .docx file.
        filename: Original filename (not used here but kept for clarity).

    Returns:
        A string containing the converted Markdown content.
    """

    # Create an in-memory file-like object from the bytes
    document_stream = io.BytesIO(document_bytes)

    # Use the conversion library to produce Markdown
    result = mammoth.convert_to_markdown(document_stream)
    markdown_text = result.value

    return markdown_text