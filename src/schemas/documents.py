"""
Document schemas — Pydantic models for document representation.

These models define the structure for documents as they flow through
the intake and normalization pipeline.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class FileType(str, Enum):
    """Supported document file types."""
    EMAIL = "email"
    PDF = "pdf"
    JSON = "json"
    UNKNOWN = "unknown"


class DocumentInput(BaseModel):
    """
    Raw document input before processing.

    Represents the initial state of a document when it enters the system.
    """
    document_id: str = Field(description="Unique identifier for this document")
    file_type: FileType = Field(description="Detected file type")
    raw_content: str = Field(description="Raw content as text")
    filename: str | None = Field(default=None, description="Original filename if uploaded")

    model_config = {"json_schema_extra": {
        "examples": [{
            "document_id": "doc-abc123",
            "file_type": "email",
            "raw_content": "From: alice@example.com\nSubject: Invoice Query\n...",
            "filename": None,
        }]
    }}


class NormalizedDocument(BaseModel):
    """
    Normalized document after intake processing.

    Contains both the raw and processed content, along with
    any metadata extracted during normalization.
    """
    document_id: str = Field(description="Unique identifier for this document")
    file_type: FileType = Field(description="Detected file type")
    raw_content: str = Field(description="Original raw content")
    normalized_content: str = Field(description="Cleaned and normalized content")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata extracted during normalization",
    )
