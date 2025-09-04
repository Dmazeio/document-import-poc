# File: src/document_classifier.py
import instructor
from openai import OpenAI
from .models import DocumentAnalysis, DocumentType

def classify_document_type(client: OpenAI, markdown_content: str) -> DocumentType:
    """
    Uses a fast AI call with Pydantic to classify if a document contains
    one or multiple meetings. This version uses a "sandwich" sample
    (start and end) for better accuracy on long documents.
    """
    instructor_client = instructor.patch(client)
    
    # Create a representative sample of the document
    sample_size = 4000 # Number of characters from the start and end
    if len(markdown_content) > sample_size * 2:
        document_sample = (
            markdown_content[:sample_size]
            + "\n\n... [CONTENT TRUNCATED] ...\n\n"
            + markdown_content[-sample_size:]
        )
    else:
        document_sample = markdown_content

    system_prompt = """
    You are a document classification expert. Your task is to determine if a document
    contains minutes from a single meeting or multiple, distinct meetings.
    Multiple meetings are often separated by top-level Markdown headings
    like '# Meeting Title' or '# Protokoll'.
    You will receive a sample of the document which includes the beginning and the end.
    """
    
    try:
        analysis = instructor_client.chat.completions.create(
            model="gpt-4o", 
            response_model=DocumentAnalysis,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze the structure of the following document sample and classify it.\n\nDOCUMENT SAMPLE:\n---\n{document_sample}\n---"} 
            ]
        )
        print(f"  - Document classified as: {analysis.document_type}. Reasoning: {analysis.reasoning}")
        return analysis.document_type
    except Exception as e:
        print(f"  - WARNING: Document classification failed: {e}. Defaulting to 'single_meeting' mode.")
        return "single_meeting"