# File: src/document_splitter.py
import instructor
from openai import OpenAI
from typing import List
from .models import MultiMeetingDocument, MeetingChunk

def split_document_into_meetings(client: OpenAI, markdown_content: str) -> List[MeetingChunk]:
    instructor_client = instructor.patch(client)
    
    try:
    
        # We send the entire document, as it needs all the info to split correctly.
        structured_document = instructor_client.chat.completions.create(
            model="gpt-4o",
            response_model=MultiMeetingDocument, # The magic again!
            messages=[
                {"role": "system", "content": "You are a document analysis expert... split the document..."},
                {"role": "user", "content": f"Analyze the following document... {markdown_content} ..."}
            ],
            max_retries=2 # Instructor will retry automatically if the AI gives a bad response
        )
        # We only return the list of meetings that were found.
        return structured_document.meetings
    except Exception as e:
        return [] # Returns an empty list on error.