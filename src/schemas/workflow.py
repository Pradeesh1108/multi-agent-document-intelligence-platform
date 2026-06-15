"""
Workflow schemas — API request/response models for the workflow endpoints.
"""

from typing import Any, Literal

from pydantic import BaseModel, Field

from src.schemas.agent_outputs import (
    ActionResult,
    ExtractedEntities,
    IntentClassification,
    RiskAnalysis,
    WorkflowDecision,
)


# ============================================================
# API Request Models
# ============================================================

class ProcessDocumentRequest(BaseModel):
    """Request body for document processing endpoint."""
    raw_text_input: str | None = Field(
        default=None,
        description="Raw text content to process (email body, JSON string, etc.)",
    )
    llm_provider: Literal["gemini", "groq"] | None = Field(
        default=None,
        description="Override the default LLM provider for this request",
    )


class RAGIngestRequest(BaseModel):
    """Request body for RAG ingestion endpoint."""
    directory: str | None = Field(
        default=None,
        description="Specific subdirectory in knowledge_base/ to ingest. "
                    "If None, ingests all directories.",
    )


# ============================================================
# API Response Models
# ============================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    llm_provider: str = ""


class WorkflowResult(BaseModel):
    """Complete workflow execution result returned to the client."""
    workflow_id: str = Field(description="Unique workflow execution ID")
    status: str = Field(description="Workflow execution status")
    document_id: str = Field(description="Document identifier")
    file_type: str = Field(description="Detected file type")
    intent: IntentClassification | None = Field(
        default=None, description="Intent classification result",
    )
    extracted_entities: ExtractedEntities | None = Field(
        default=None, description="Extracted entities",
    )
    retrieved_context: list[str] = Field(
        default_factory=list,
        description="Retrieved knowledge context from RAG",
    )
    risk_analysis: RiskAnalysis | None = Field(
        default=None, description="Risk analysis result",
    )
    decision: WorkflowDecision | None = Field(
        default=None, description="Workflow decision",
    )
    actions: list[ActionResult] = Field(
        default_factory=list,
        description="List of executed actions",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Any errors encountered during processing",
    )
    processing_time_ms: float = Field(
        default=0.0,
        description="Total processing time in milliseconds",
    )

    model_config = {"json_schema_extra": {
        "examples": [{
            "workflow_id": "wf-abc123",
            "status": "completed",
            "document_id": "doc-xyz789",
            "file_type": "email",
            "intent": {
                "intent": "complaint",
                "confidence": 0.95,
                "reasoning": "Email contains strong complaint language about service issues",
            },
            "extracted_entities": {
                "entity_type": "complaint",
                "entities": {
                    "customer_name": "Alice Johnson",
                    "issue_summary": "Service outage on production systems",
                    "urgency": "high",
                },
                "confidence": 0.88,
            },
            "retrieved_context": ["CRM escalation policy requires immediate response..."],
            "risk_analysis": {
                "risk_score": 0.7,
                "risk_level": "high",
                "risk_factors": ["High urgency complaint", "Production impact"],
                "recommended_action": "Immediate CRM escalation",
                "explanation": "Customer reporting production outage requires priority handling",
            },
            "decision": {
                "decision": "escalate_to_crm",
                "confidence": 0.94,
                "reasoning": "High-priority customer complaint with production impact",
                "priority": "high",
            },
            "actions": [{
                "action_type": "crm_ticket_created",
                "status": "success",
                "details": {"ticket_id": "CRM-001"},
                "timestamp": "2025-06-01T10:00:00Z",
            }],
            "errors": [],
            "processing_time_ms": 3450.5,
        }]
    }}
