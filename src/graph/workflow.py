"""
LangGraph Workflow — Compiles the multi-agent StateGraph.

Defines the complete document processing pipeline:
    START → Intake → Intent → Extraction → Knowledge → Risk → Decision → Action → END
"""

from langgraph.graph import END, START, StateGraph

from src.core.logging import get_logger
from src.graph.nodes import (
    action_node,
    decision_node,
    extraction_node,
    intake_node,
    intent_node,
    knowledge_node,
    risk_node,
)
from src.graph.state import WorkflowState

logger = get_logger(__name__)


def build_workflow() -> StateGraph:
    """
    Build and compile the multi-agent workflow graph.

    Returns:
        Compiled LangGraph StateGraph ready for invocation.
    """
    logger.info("Building LangGraph workflow...")

    graph = StateGraph(WorkflowState)

    # ── Register Nodes ──────────────────────────────────────────
    graph.add_node("intake", intake_node)
    graph.add_node("intent", intent_node)
    graph.add_node("extraction", extraction_node)
    graph.add_node("knowledge", knowledge_node)
    graph.add_node("risk", risk_node)
    graph.add_node("decision", decision_node)
    graph.add_node("action", action_node)

    # ── Define Edges (Linear Pipeline) ──────────────────────────
    graph.add_edge(START, "intake")
    graph.add_edge("intake", "intent")
    graph.add_edge("intent", "extraction")
    graph.add_edge("extraction", "knowledge")
    graph.add_edge("knowledge", "risk")
    graph.add_edge("risk", "decision")
    graph.add_edge("decision", "action")
    graph.add_edge("action", END)

    # ── Compile ─────────────────────────────────────────────────
    compiled = graph.compile()
    logger.info(
        "LangGraph workflow compiled: "
        "START → Intake → Intent → Extraction → Knowledge → Risk → Decision → Action → END"
    )

    return compiled
