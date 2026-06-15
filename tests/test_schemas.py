"""
Tests for Pydantic schema validation.
"""

import pytest
from pydantic import ValidationError

from src.schemas.agent_outputs import (
    ActionResult,
    ComplaintEntities,
    ExtractedEntities,
    IntentClassification,
    InvoiceEntities,
    RiskAnalysis,
    WorkflowDecision,
)
from src.schemas.documents import DocumentInput, FileType, NormalizedDocument
from src.schemas.workflow import ProcessDocumentRequest, WorkflowResult


class TestDocumentSchemas:
    """Tests for document-related schemas."""

    def test_file_type_enum(self):
        assert FileType.EMAIL.value == "email"
        assert FileType.PDF.value == "pdf"
        assert FileType.JSON.value == "json"
        assert FileType.UNKNOWN.value == "unknown"

    def test_document_input_valid(self):
        doc = DocumentInput(
            document_id="doc-123",
            file_type=FileType.EMAIL,
            raw_content="test content",
        )
        assert doc.document_id == "doc-123"
        assert doc.file_type == FileType.EMAIL
        assert doc.filename is None

    def test_normalized_document(self):
        doc = NormalizedDocument(
            document_id="doc-123",
            file_type=FileType.PDF,
            raw_content="raw",
            normalized_content="clean",
            metadata={"word_count": 42},
        )
        assert doc.normalized_content == "clean"
        assert doc.metadata["word_count"] == 42


class TestAgentOutputSchemas:
    """Tests for agent output schemas."""

    def test_intent_classification_valid(self):
        intent = IntentClassification(
            intent="complaint",
            confidence=0.95,
            reasoning="Strong complaint language detected",
        )
        assert intent.intent == "complaint"
        assert intent.confidence == 0.95

    def test_intent_classification_invalid_confidence(self):
        with pytest.raises(ValidationError):
            IntentClassification(
                intent="complaint",
                confidence=1.5,  # Out of range
                reasoning="test",
            )

    def test_intent_classification_invalid_intent(self):
        with pytest.raises(ValidationError):
            IntentClassification(
                intent="invalid_intent",  # Not in Literal
                confidence=0.5,
                reasoning="test",
            )

    def test_invoice_entities(self):
        entities = InvoiceEntities(
            invoice_id="INV-001",
            vendor="Acme Corp",
            amount=1250.75,
            currency="USD",
        )
        assert entities.invoice_id == "INV-001"
        assert entities.amount == 1250.75

    def test_complaint_entities(self):
        entities = ComplaintEntities(
            customer_name="Alice",
            issue_summary="Service outage",
            urgency="high",
        )
        assert entities.urgency == "high"

    def test_complaint_entities_invalid_urgency(self):
        with pytest.raises(ValidationError):
            ComplaintEntities(
                issue_summary="test",
                urgency="super_urgent",  # Not in Literal
            )

    def test_risk_analysis_valid(self):
        risk = RiskAnalysis(
            risk_score=0.7,
            risk_level="high",
            risk_factors=["High-value transaction"],
            recommended_action="Manual review",
            explanation="Multiple risk indicators found",
        )
        assert risk.risk_score == 0.7
        assert risk.risk_level == "high"

    def test_risk_analysis_score_bounds(self):
        with pytest.raises(ValidationError):
            RiskAnalysis(
                risk_score=1.5,  # Over 1.0
                risk_level="high",
                risk_factors=[],
                recommended_action="test",
                explanation="test",
            )

    def test_workflow_decision(self):
        decision = WorkflowDecision(
            decision="escalate_to_crm",
            confidence=0.94,
            reasoning="High-priority customer complaint",
            priority="high",
        )
        assert decision.decision == "escalate_to_crm"

    def test_action_result(self):
        action = ActionResult(
            action_type="crm_ticket_created",
            status="success",
            details={"ticket_id": "CRM-001"},
            timestamp="2025-06-01T10:00:00Z",
        )
        assert action.status == "success"

    def test_extracted_entities_wrapper(self):
        entities = ExtractedEntities(
            entity_type="invoice",
            entities={"invoice_id": "INV-001", "amount": 1000},
            confidence=0.85,
        )
        assert entities.entity_type == "invoice"
        assert entities.entities["amount"] == 1000


class TestWorkflowSchemas:
    """Tests for workflow API schemas."""

    def test_process_document_request_defaults(self):
        req = ProcessDocumentRequest()
        assert req.raw_text_input is None
        assert req.llm_provider is None

    def test_process_document_request_with_provider(self):
        req = ProcessDocumentRequest(
            raw_text_input="test content",
            llm_provider="groq",
        )
        assert req.llm_provider == "groq"

    def test_workflow_result_minimal(self):
        result = WorkflowResult(
            workflow_id="wf-123",
            status="completed",
            document_id="doc-456",
            file_type="email",
        )
        assert result.status == "completed"
        assert result.actions == []
        assert result.errors == []

    def test_workflow_result_full(self):
        result = WorkflowResult(
            workflow_id="wf-123",
            status="completed",
            document_id="doc-456",
            file_type="email",
            intent=IntentClassification(
                intent="complaint",
                confidence=0.95,
                reasoning="test",
            ),
            risk_analysis=RiskAnalysis(
                risk_score=0.7,
                risk_level="high",
                risk_factors=["test"],
                recommended_action="review",
                explanation="test",
            ),
            processing_time_ms=3450.5,
        )
        assert result.intent.intent == "complaint"
        assert result.risk_analysis.risk_score == 0.7
