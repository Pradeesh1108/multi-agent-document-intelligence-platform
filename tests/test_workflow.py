"""
Tests for LangGraph workflow construction.
"""

from src.graph.state import WorkflowState
from src.graph.workflow import build_workflow


class TestWorkflowConstruction:
    """Tests for workflow graph building."""

    def test_build_workflow_returns_compiled_graph(self):
        """Workflow should compile without errors."""
        workflow = build_workflow()
        assert workflow is not None

    def test_workflow_state_type(self):
        """WorkflowState should be a valid TypedDict."""
        # Verify all required keys exist in annotations
        annotations = WorkflowState.__annotations__
        expected_keys = [
            "document_id", "file_type", "raw_content", "normalized_content",
            "intent", "extracted_entities", "retrieved_context",
            "risk_analysis", "decision", "actions", "metadata",
            "errors", "llm_provider",
        ]
        for key in expected_keys:
            assert key in annotations, f"Missing key in WorkflowState: {key}"

    def test_initial_state_creation(self):
        """Should be able to create a valid initial state dict."""
        state: WorkflowState = {
            "document_id": "doc-test",
            "file_type": "email",
            "raw_content": "test content",
            "normalized_content": "",
            "intent": None,
            "extracted_entities": None,
            "retrieved_context": [],
            "risk_analysis": None,
            "decision": None,
            "actions": [],
            "metadata": {},
            "errors": [],
            "llm_provider": None,
        }
        assert state["document_id"] == "doc-test"
        assert state["errors"] == []
