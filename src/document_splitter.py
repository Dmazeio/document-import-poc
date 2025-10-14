
import instructor
from openai import OpenAI
from typing import List

from .models import MultiItemDocument, DocumentChunk


def split_document_into_items(client: OpenAI, markdown_content: str, root_object_name: str) -> List[DocumentChunk]:
    """
    Split a document into a list of distinct items, where each item
    is a self-contained part of the document (e.g. a single meeting record or a risk assessment).
    """
    instructor_client = instructor.patch(client)
    

    system_prompt = f"""
    You are a document analysis and segmentation expert. Your task is to split the following Markdown document into a list of distinct, self-contained '{root_object_name}' items.
    
    Each new item almost always starts with a top-level Markdown heading (a single '#').
    You must capture the title from the heading and all the content that belongs to that item until the next top-level heading or the end of the document.
    """
    
    try:
        structured_document = instructor_client.chat.completions.create(
            model="gpt-4o",
            response_model=MultiItemDocument,  # Uses the new structured response model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze and split the following document:\n\n{markdown_content}"}
            ],
            max_retries=2
        )
        # Return the list of items
        return structured_document.items
    except Exception as e:
        print(f"  - ERROR: Document splitting failed: {e}")
        return []
