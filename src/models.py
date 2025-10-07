# File: src/models.py (GENERALIZED VERSION)
from pydantic import BaseModel, Field
from typing import List, Literal

# Endre navn fra DocumentType til noe mer generelt
DocumentStructureType = Literal["single_item", "multiple_items"]

class DocumentAnalysis(BaseModel):
    # Bruk den nye, generelle typen
    document_type: DocumentStructureType
    reasoning: str


class DocumentChunk(BaseModel):
    # Endre feltnavn for å være generelle
    item_title: str
    item_content: str

class MultiItemDocument(BaseModel):
    # Bruk den nye DocumentChunk og et generelt feltnavn
    items: List[DocumentChunk]