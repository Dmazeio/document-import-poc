from typing import List
from .ai_client import AIClient
from .models import MultiItemDocument, DocumentChunk

def split_document_into_items(ai_client: AIClient, markdown_content: str, root_object_name: str) -> List[DocumentChunk]:
    """
    Uses the centralized AIClient to split a document into a list of distinct items.
    """
    system_prompt = f"""
    You are a document analysis and segmentation expert. Your task is to split the following Markdown document into a list of distinct, self-contained '{root_object_name}' items.
    
    Each new item almost always starts with a top-level Markdown heading (a single '#').
    You must capture the title from the heading and all the content that belongs to that item until the next top-level heading or the end of the document.
    """
    
    user_prompt = f"Analyze and split the following document:\n\n{markdown_content}"
    
    try:
        # Use the centralized method with a response_model
        structured_document = ai_client.get_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=MultiItemDocument,
            model="gpt-4o",
            max_retries=2
        )
        return structured_document.items
    except Exception as e:
        print(f"  - ERROR: Document splitting failed: {e}")
        return []