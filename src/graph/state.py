"""
Workflow State — Strongly-typed state for the LangGraph pipeline.

Defines the complete state schema that flows through all agent nodes.
Uses TypedDict for LangGraph compatibility.
"""

from typing import Any, TypedDict


class WorkflowState(TypedDict):
    """
    Complete workflow state passed through all LangGraph nodes.

    Each agent node reads relevant fields and writes its results
    back into the state via partial update dicts.
    """

    # --- Document Identity ---
    document_id: str
    """Unique identifier for the document being processed."""

    file_type: str
    """Detected file type (email, pdf, json, unknown)."""

    # --- Content ---
    raw_content: str
    """Original raw content as received."""

    normalized_content: str
    """Cleaned and normalized content from Intake Agent."""

    # --- Agent Outputs ---
    intent: dict | None
    """Intent classification result (IntentClassification dict)."""

    extracted_entities: dict | None
    """Extracted entities (ExtractedEntities dict)."""

    retrieved_context: list[str]
    """Retrieved knowledge chunks from RAG."""

    risk_analysis: dict | None
    """Risk analysis result (RiskAnalysis dict)."""

    decision: dict | None
    """Final workflow decision (WorkflowDecision dict)."""

    actions: list[dict]
    """List of executed action results (ActionResult dicts)."""

    # --- Metadata ---
    metadata: dict[str, Any]
    """Additional workflow metadata (workflow_id, filename, etc.)."""

    errors: list[str]
    """Errors accumulated during processing."""

    llm_provider: str | None
    """Optional LLM provider override for this workflow run."""

    api_key: str | None
    """Optional API key override from the frontend for demo purposes."""
