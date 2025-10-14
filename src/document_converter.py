import os
import tempfile
from markitdown import MarkItDown

def convert_file_to_markdown(document_bytes: bytes, filename: str) -> str:
    """
    Converts in-memory bytes to Markdown using the 'markitdown' library.
    Writes the bytes to a temporary file because the library expects a file path.
    """
    print(f"  - Converting '{filename}' using the MarkItDown library...")

    # tempfile creates a temporary directory which is removed after use.
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. Create a full path to a temporary file INSIDE the temporary directory.
        # Keep the original filename so markitdown can detect the type.
        temp_input_path = os.path.join(temp_dir, filename)

        try:
            # 2. Write the in-memory bytes to the temporary file.
            with open(temp_input_path, 'wb') as f:
                f.write(document_bytes)

            # 3. Create an instance of the converter.
            md_converter = MarkItDown()

            # 4. Call convert() with the PATH to the temporary file.
            result = md_converter.convert(temp_input_path)
            
            # 5. Extract the final Markdown content.
            markdown_content = result.text_content
            
            print(f"  - Conversion of '{filename}' successful.")
            return markdown_content

        except Exception as e:
            # If something fails, log it and re-raise so the caller can handle it.
            print(f"  - ERROR: The MarkItDown library failed to convert {filename}.")
            print(f"    Reason: {e}")
            raise e