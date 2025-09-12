# File: src/document_splitter.py (GENERALIZED VERSION)
import instructor
from openai import OpenAI
from typing import List
# Importer de nye, generelle modellene
from .models import MultiItemDocument, DocumentChunk

def split_document_into_items(client: OpenAI, markdown_content: str, root_object_name: str) -> List[DocumentChunk]:
    """
    Splitter et dokument i en liste av "elementer", der hvert element
    er en selvstendig del av dokumentet (f.eks. ett møtereferat, en risikovurdering).
    """
    instructor_client = instructor.patch(client)
    
    # GENERALISERT PROMPT:
    system_prompt = f"""
    You are a document analysis and segmentation expert. Your task is to split the following Markdown document into a list of distinct, self-contained '{root_object_name}' items.
    
    Each new item almost always starts with a top-level Markdown heading (a single '#').
    You must capture the title from the heading and all the content that belongs to that item until the next top-level heading or the end of the document.
    """
    
    try:
        structured_document = instructor_client.chat.completions.create(
            model="gpt-4o",
            response_model=MultiItemDocument, # Bruker den nye modellen
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze and split the following document:\n\n{markdown_content}"}
            ],
            max_retries=2
        )
        # Returnerer listen med generelle "items"
        return structured_document.items
    except Exception as e:
        print(f"  - ERROR: Document splitting failed: {e}")
        return []
