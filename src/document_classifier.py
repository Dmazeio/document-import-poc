from .ai_client import AIClient
from .models import DocumentAnalysis, DocumentStructureType

def classify_document_type(ai_client: AIClient, markdown_content: str, root_object_name: str) -> DocumentStructureType:
    """
    Uses the centralized AIClient to classify whether a document contains a single
    or multiple distinct '{root_object_name}' items.
    """
    sample_size = 4000
    if len(markdown_content) > sample_size * 2:
        document_sample = (
            markdown_content[:sample_size]
            + "\n\n... [CONTENT TRUNCATED] ...\n\n"
            + markdown_content[-sample_size:]
        )
    else:
        document_sample = markdown_content

    system_prompt = f"""
    You are a document classification expert. Your task is to determine if a document
    contains a single, coherent '{root_object_name}' item or a collection of multiple, distinct '{root_object_name}' items.
    
    Multiple items are almost always separated by top-level Markdown headings (e.g., '# Title of Item 1', '# Title of Item 2').
    If you see multiple top-level headings that seem to describe separate, self-contained entries, classify it as 'multiple_items'.
    Otherwise, classify it as 'single_item'.
    """
    
    user_prompt = f"Analyze the structure of the following document sample and classify it.\n\nDOCUMENT SAMPLE:\n---\n{document_sample}\n---"
    
    try:
        # Use the centralized method with a response_model
        analysis = ai_client.get_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=DocumentAnalysis,
            model="gpt-4o"
        )
        print(f"  - Document classified as: {analysis.document_type}. Reasoning: {analysis.reasoning}")
        return analysis.document_type
    except Exception as e:
        print(f"  - WARNING: Document classification failed: {e}. Defaulting to 'single_item' mode.")
        return "single_item"