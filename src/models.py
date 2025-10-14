from pydantic import BaseModel, Field
from typing import List, Literal

DocumentStructureType = Literal["single_item", "multiple_items"]

class DocumentAnalysis(BaseModel):
    document_type: DocumentStructureType
    reasoning: str


class DocumentChunk(BaseModel):
    item_title: str
    item_content: str

class MultiItemDocument(BaseModel):
    items: List[DocumentChunk]