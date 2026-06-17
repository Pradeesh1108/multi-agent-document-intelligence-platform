"""
Graph Edges — Edge conditions for conditional routing.

Currently uses a linear pipeline (START → Intake → Intent → Extraction →
Knowledge → Risk → Decision → Action → END).

Conditional edges can be added here for more complex routing logic,
e.g., skipping knowledge retrieval based on intent or short-circuiting
on critical errors.
"""

from src.core.logging import get_logger
from src.graph.state import WorkflowState

logger = get_logger(__name__)


def should_continue_after_intake(state: WorkflowState) -> str:
    """
    Determine if workflow should continue after intake.

    Returns "continue" to proceed to intent classification,
    or "abort" if the document is fatally invalid.
    """
    if not state.get("normalized_content", "").strip():
        logger.warning("Empty normalized content — aborting workflow")
        return "abort"
    return "continue"


def should_skip_knowledge(state: WorkflowState) -> str:
    """
    Determine if knowledge retrieval should be skipped.

    Could be used to skip RAG for certain intents where
    knowledge retrieval adds no value.
    """
    intent = state.get("intent", {})
    if isinstance(intent, dict):
        intent_val = intent.get("intent", "other")
    else:
        intent_val = "other"
    
    if intent_val in ("other", "general_inquiry"):
        logger.info(f"Skipping knowledge retrieval for intent: {intent_val}")
        return "skip"
        
    return "retrieve"
