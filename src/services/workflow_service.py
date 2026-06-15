"""
Workflow Service — Orchestrates document processing workflows.

Bridges the FastAPI endpoints with the LangGraph workflow engine.
Handles input preparation, workflow execution, and result conversion.
"""

import time
import uuid
from typing import Any

from src.core.logging import get_logger
from src.graph.workflow import build_workflow
from src.schemas.agent_outputs import (
    ActionResult,
    ExtractedEntities,
    IntentClassification,
    RiskAnalysis,
    WorkflowDecision,
)
from src.schemas.workflow import WorkflowResult
from src.services.document_parser import detect_file_type, extract_pdf_text

logger = get_logger(__name__)

# In-memory workflow status store
# In production, replace with Redis, a database, or a proper state store.
_workflow_store: dict[str, dict[str, Any]] = {}


class WorkflowService:
    """
    Service that manages document processing workflow execution.

    Converts raw inputs into workflow state, runs the LangGraph pipeline,
    and transforms results into API responses.
    """

    def __init__(self) -> None:
        """Initialize the workflow service with a compiled LangGraph."""
        self._workflow = build_workflow()
        logger.info("WorkflowService initialized with compiled LangGraph workflow")

    async def process_text(
        self,
        raw_text: str,
        llm_provider: str | None = None,
        filename: str | None = None,
    ) -> WorkflowResult:
        """
        Process raw text input through the full agent workflow.

        Args:
            raw_text: Raw text content (email, JSON, pasted text, etc.).
            llm_provider: Optional LLM provider override ("gemini" or "groq").
            filename: Optional original filename for file type detection.

        Returns:
            WorkflowResult with all agent outputs.
        """
        document_id = f"doc-{uuid.uuid4().hex[:12]}"
        workflow_id = f"wf-{uuid.uuid4().hex[:12]}"

        logger.info(f"Starting workflow {workflow_id} for document {document_id}")

        # Detect file type
        file_type = detect_file_type(raw_text, filename)

        # Build initial state
        initial_state = {
            "document_id": document_id,
            "file_type": file_type.value,
            "raw_content": raw_text,
            "normalized_content": "",
            "intent": None,
            "extracted_entities": None,
            "retrieved_context": [],
            "risk_analysis": None,
            "decision": None,
            "actions": [],
            "metadata": {
                "workflow_id": workflow_id,
                "filename": filename,
                "source": "api_text_input" if not filename else "api_file_upload",
            },
            "errors": [],
            "llm_provider": llm_provider,
        }

        # Track in store
        _workflow_store[workflow_id] = {
            "status": "running",
            "document_id": document_id,
            "started_at": time.time(),
        }

        # Run the workflow
        start_time = time.time()
        try:
            final_state = self._workflow.invoke(initial_state)
            elapsed_ms = (time.time() - start_time) * 1000

            _workflow_store[workflow_id]["status"] = "completed"
            _workflow_store[workflow_id]["completed_at"] = time.time()

            logger.info(
                f"Workflow {workflow_id} completed in {elapsed_ms:.1f}ms"
            )

            return self._state_to_result(final_state, workflow_id, elapsed_ms)

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            _workflow_store[workflow_id]["status"] = "failed"
            _workflow_store[workflow_id]["error"] = str(e)

            logger.error(f"Workflow {workflow_id} failed after {elapsed_ms:.1f}ms: {e}")

            return WorkflowResult(
                workflow_id=workflow_id,
                status="failed",
                document_id=document_id,
                file_type=file_type.value,
                errors=[str(e)],
                processing_time_ms=elapsed_ms,
            )

    async def process_file(
        self,
        file_path: str,
        filename: str,
        llm_provider: str | None = None,
    ) -> WorkflowResult:
        """
        Process an uploaded file through the workflow.

        Args:
            file_path: Path to the uploaded file on disk.
            filename: Original filename.
            llm_provider: Optional LLM provider override.

        Returns:
            WorkflowResult with all agent outputs.
        """
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

        if ext == "pdf":
            raw_text = extract_pdf_text(file_path)
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()

        return await self.process_text(raw_text, llm_provider, filename)

    def get_workflow_status(self, workflow_id: str) -> dict[str, Any] | None:
        """
        Get the status of a workflow execution.

        Args:
            workflow_id: The workflow ID to look up.

        Returns:
            Status dict or None if not found.
        """
        return _workflow_store.get(workflow_id)

    def _state_to_result(
        self,
        state: dict[str, Any],
        workflow_id: str,
        elapsed_ms: float,
    ) -> WorkflowResult:
        """Convert the final LangGraph state dict into a WorkflowResult."""
        # Parse structured outputs from state dicts
        intent = None
        if state.get("intent"):
            try:
                intent = IntentClassification(**state["intent"])
            except Exception:
                intent = None

        entities = None
        if state.get("extracted_entities"):
            try:
                entities = ExtractedEntities(**state["extracted_entities"])
            except Exception:
                entities = None

        risk = None
        if state.get("risk_analysis"):
            try:
                risk = RiskAnalysis(**state["risk_analysis"])
            except Exception:
                risk = None

        decision = None
        if state.get("decision"):
            try:
                decision = WorkflowDecision(**state["decision"])
            except Exception:
                decision = None

        actions = []
        for action_dict in state.get("actions", []):
            try:
                actions.append(ActionResult(**action_dict))
            except Exception:
                continue

        return WorkflowResult(
            workflow_id=workflow_id,
            status="completed",
            document_id=state.get("document_id", ""),
            file_type=state.get("file_type", "unknown"),
            intent=intent,
            extracted_entities=entities,
            retrieved_context=state.get("retrieved_context", []),
            risk_analysis=risk,
            decision=decision,
            actions=actions,
            errors=state.get("errors", []),
            processing_time_ms=elapsed_ms,
        )
