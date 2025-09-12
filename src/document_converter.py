# File: src/document_converter.py

from markitdown import MarkItDown

def convert_file_to_markdown(file_path: str) -> str:
    """
    Converts any supported file (PDF, DOCX, etc.) to a structured
    Markdown string using the MarkItDown library.
    
    This function replaces the old PDF-specific processor.
    """
    try:
        # Initialize the converter
        converter = MarkItDown()
        
        # Convert the file to Markdown
        markdown_object = converter.convert(file_path)
        
        # Convert the result to a plain text string before returning it.
        markdown_content = str(markdown_object)
        
        return markdown_content
        
    except FileNotFoundError:
        # Returns a dictionary with an error message for consistent error handling
        # We return a dictionary here to avoid a crash if the file is not found.
        # This is technically not a string, but main.py checks for this.
        return {"error": f"File not found at: {file_path}"}
    except Exception as e:
        return {"error": f"An error occurred while converting the file to Markdown: {e}"}
    