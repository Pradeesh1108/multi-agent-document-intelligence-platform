"""
Agent output schemas — Structured Pydantic models for all agent outputs.

These schemas are used with LangChain's `with_structured_output()` to enforce
type-safe, validated outputs from LLM calls. No manual JSON parsing needed.
"""

from typing import Any, Literal

from pydantic import BaseModel, Field


# ============================================================
# Intent Agent Outputs
# ============================================================

class IntentClassification(BaseModel):
    """Structured output from the Intent Agent."""
    intent: Literal[
        "complaint",
        "invoice",
        "rfq",
        "compliance",
        "fraud_risk",
        "support_request",
        "general_inquiry",
        "other",
    ] = Field(description="The classified business intent of the document")
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score for the classification (0.0 to 1.0)",
    )
    reasoning: str = Field(
        description="Brief explanation of why this intent was chosen",
    )


# ============================================================
# Extraction Agent Outputs
# ============================================================

class InvoiceEntities(BaseModel):
    """Entities extracted from invoice documents."""
    invoice_id: str | None = Field(default=None, description="Invoice identifier")
    vendor: str | None = Field(default=None, description="Vendor or supplier name")
    amount: float | None = Field(default=None, description="Total invoice amount")
    currency: str | None = Field(default=None, description="Currency code (e.g., USD, EUR)")
    due_date: str | None = Field(default=None, description="Payment due date")
    line_items: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Individual line items on the invoice",
    )


class ComplaintEntities(BaseModel):
    """Entities extracted from complaint documents."""
    customer_name: str | None = Field(default=None, description="Name of the complainant")
    customer_email: str | None = Field(default=None, description="Email of the complainant")
    issue_summary: str = Field(description="Concise summary of the complaint")
    urgency: Literal["low", "medium", "high", "critical"] = Field(
        description="Urgency level of the complaint",
    )
    category: str | None = Field(
        default=None,
        description="Category of the complaint (e.g., billing, technical, service)",
    )


class RFQEntities(BaseModel):
    """Entities extracted from Request for Quote documents."""
    requester_name: str | None = Field(default=None, description="Name of the requester")
    requester_email: str | None = Field(default=None, description="Email of the requester")
    products_services: list[str] = Field(
        default_factory=list,
        description="Products or services being requested",
    )
    quantity: str | None = Field(default=None, description="Requested quantity")
    deadline: str | None = Field(default=None, description="Quote deadline")
    budget: str | None = Field(default=None, description="Estimated budget if mentioned")


class PDFEntities(BaseModel):
    """Entities extracted from PDF documents."""
    document_type: str = Field(description="Type of document (invoice, policy, report, etc.)")
    title: str | None = Field(default=None, description="Document title if found")
    summary: str = Field(description="Concise summary of the document content")
    key_entities: list[str] = Field(
        default_factory=list,
        description="Key entities, terms, or concepts found",
    )
    regulatory_keywords: list[str] = Field(
        default_factory=list,
        description="Regulatory keywords found (e.g., GDPR, HIPAA, SOX)",
    )


class GenericEntities(BaseModel):
    """Entities extracted from documents with no specific schema."""
    summary: str = Field(description="Summary of the document content")
    key_fields: dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value pairs of important fields",
    )
    entities_found: list[str] = Field(
        default_factory=list,
        description="Named entities found in the document",
    )


class ExtractedEntities(BaseModel):
    """Wrapper for extracted entities with metadata."""
    entity_type: str = Field(description="Type of entity schema used")
    entities: dict[str, Any] = Field(description="Extracted entity data")
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence in extraction accuracy",
    )


# ============================================================
# Risk Agent Outputs
# ============================================================

class RiskAnalysis(BaseModel):
    """Structured output from the Risk Agent."""
    risk_score: float = Field(
        ge=0.0, le=1.0,
        description="Overall risk score (0.0 = no risk, 1.0 = maximum risk)",
    )
    risk_level: Literal["low", "medium", "high", "critical"] = Field(
        description="Human-readable risk level",
    )
    risk_factors: list[str] = Field(
        default_factory=list,
        description="Identified risk factors",
    )
    recommended_action: str = Field(
        description="Recommended course of action based on risk assessment",
    )
    explanation: str = Field(
        description="Detailed explanation of the risk analysis",
    )


# ============================================================
# Decision Agent Outputs
# ============================================================

class WorkflowDecision(BaseModel):
    """Structured output from the Decision Agent."""
    decision: str = Field(
        description="The workflow decision (e.g., 'escalate_to_crm', 'flag_for_review')",
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence in the decision",
    )
    reasoning: str = Field(
        description="Detailed reasoning for the decision",
    )
    priority: Literal["low", "medium", "high", "critical"] = Field(
        description="Priority level for the action",
    )


# ============================================================
# Action Agent Outputs
# ============================================================

class ActionResult(BaseModel):
    """Result of a single executed action."""
    action_type: str = Field(description="Type of action executed")
    status: Literal["success", "failed", "skipped"] = Field(
        description="Execution status",
    )
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Action-specific details and response data",
    )
    timestamp: str = Field(description="ISO timestamp of when the action was executed")
