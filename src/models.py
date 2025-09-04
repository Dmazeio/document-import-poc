# File: src/models.py
from pydantic import BaseModel, Field
from typing import List, Literal

# This is like a multiple-choice question for the AI. The answer MUST be one of these two.
DocumentType = Literal["single_meeting", "multiple_meetings"]

class DocumentAnalysis(BaseModel):
    # The AI MUST return an object that has these two fields:
    document_type: DocumentType # The answer to the multiple-choice question.
    reasoning: str             # A brief explanation.


class MeetingChunk(BaseModel):
    # Each section MUST have a title and the actual content.
    meeting_title: str
    meeting_content: str

class MultiMeetingDocument(BaseModel):
    # The entire response from the AI MUST be a single object with one field:
    # 'meetings', which is a LIST of 'MeetingChunk' objects.
    meetings: List[MeetingChunk]