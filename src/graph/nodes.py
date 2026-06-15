"""
Graph Nodes — Node functions that wrap each agent for LangGraph.

Each node function:
    1. Reads relevant fields from WorkflowState
    2. Calls the corresponding agent
    3. Returns a partial state update dict

LangGraph merges the returned dict into the workflow state automatically.
"""

from src.agents.action_agent import ActionAgent
from src.agents.decision_agent import DecisionAgent
from src.agents.extraction_agent import ExtractionAgent
from src.agents.intake_agent import IntakeAgent
from src.agents.intent_agent import IntentAgent
from src.agents.knowledge_agent import KnowledgeAgent
from src.agents.risk_agent import RiskAgent
from src.core.logging import get_logger
from src.graph.state import WorkflowState

logger = get_logger(__name__)


def _clean_error(e: Exception) -> str:
    """Clean up verbose LLM API errors for the UI."""
    msg = str(e)
    if "API_KEY_INVALID" in msg or "API key not valid" in msg or "401" in msg or "authentication" in msg.lower():
        raise ValueError("Invalid API key provided. Please check your credentials.")
    if "Invalid API key provided" in msg:
        raise ValueError("Invalid API key provided. Please check your credentials.")
    # Truncate very long errors
    if len(msg) > 200:
        return msg[:197] + "..."
    return msg


def intake_node(state: WorkflowState) -> dict:
    """
    Intake Node — Normalize and validate the incoming document.

    Reads: raw_content, file_type
    Writes: normalized_content, metadata, errors
    """
    logger.info("━━━ Node: Intake Agent ━━━")
    agent = IntakeAgent()
    result = agent.process(state["raw_content"], state["file_type"])

    # Merge metadata
    current_metadata = state.get("metadata", {})
    current_metadata.update(result.get("metadata", {}))

    # Accumulate errors
    current_errors = list(state.get("errors", []))
    current_errors.extend(result.get("errors", []))

    return {
        "normalized_content": result.get("normalized_content", state["raw_content"]),
        "metadata": current_metadata,
        "errors": current_errors,
    }


def intent_node(state: WorkflowState) -> dict:
    """
    Intent Node — Classify the document's business intent.

    Reads: normalized_content, file_type, llm_provider
    Writes: intent
    """
    logger.info("━━━ Node: Intent Agent ━━━")
    agent = IntentAgent()

    try:
        result = agent.process(
            normalized_content=state["normalized_content"],
            file_type=state["file_type"],
            llm_provider=state.get("llm_provider"),
            api_key=state.get("api_key"),
        )
        return {"intent": result}
    except Exception as e:
        clean_err = _clean_error(e)
        logger.error(f"Intent node failed: {e}")
        errors = list(state.get("errors", []))
        errors.append(f"Intent classification failed: {clean_err}")
        return {
            "intent": {"intent": "other", "confidence": 0.0, "reasoning": clean_err},
            "errors": errors,
        }


def extraction_node(state: WorkflowState) -> dict:
    """
    Extraction Node — Extract structured entities based on intent.

    Reads: normalized_content, intent, file_type, llm_provider
    Writes: extracted_entities
    """
    logger.info("━━━ Node: Extraction Agent ━━━")
    agent = ExtractionAgent()

    intent_value = "other"
    if state.get("intent"):
        intent_value = state["intent"].get("intent", "other")

    try:
        result = agent.process(
            normalized_content=state["normalized_content"],
            intent=intent_value,
            file_type=state["file_type"],
            llm_provider=state.get("llm_provider"),
            api_key=state.get("api_key"),
        )
        return {"extracted_entities": result}
    except Exception as e:
        clean_err = _clean_error(e)
        logger.error(f"Extraction node failed: {e}")
        errors = list(state.get("errors", []))
        errors.append(f"Entity extraction failed: {clean_err}")
        return {
            "extracted_entities": {
                "entity_type": intent_value,
                "entities": {"error": clean_err},
                "confidence": 0.0,
            },
            "errors": errors,
        }


def knowledge_node(state: WorkflowState) -> dict:
    """
    Knowledge Node — Retrieve relevant business knowledge via RAG.

    Reads: normalized_content, intent
    Writes: retrieved_context
    """
    logger.info("━━━ Node: Knowledge Agent ━━━")
    agent = KnowledgeAgent()

    intent_value = "other"
    if state.get("intent"):
        intent_value = state["intent"].get("intent", "other")

    result = agent.process(
        normalized_content=state["normalized_content"],
        intent=intent_value,
    )

    return {"retrieved_context": result.get("retrieved_context", [])}


def risk_node(state: WorkflowState) -> dict:
    """
    Risk Node — Analyze document risk factors.

    Reads: normalized_content, intent, extracted_entities, retrieved_context, llm_provider
    Writes: risk_analysis
    """
    logger.info("━━━ Node: Risk Agent ━━━")
    agent = RiskAgent()

    try:
        result = agent.process(
            normalized_content=state["normalized_content"],
            intent=state.get("intent"),
            extracted_entities=state.get("extracted_entities"),
            retrieved_context=state.get("retrieved_context", []),
            llm_provider=state.get("llm_provider"),
            api_key=state.get("api_key"),
        )
        return {"risk_analysis": result}
    except Exception as e:
        clean_err = _clean_error(e)
        logger.error(f"Risk node failed: {e}")
        errors = list(state.get("errors", []))
        errors.append(f"Risk analysis failed: {clean_err}")
        return {
            "risk_analysis": {
                "risk_score": 0.5,
                "risk_level": "medium",
                "risk_factors": [clean_err],
                "recommended_action": "Manual review",
                "explanation": f"Risk analysis error: {clean_err}",
            },
            "errors": errors,
        }


def decision_node(state: WorkflowState) -> dict:
    """
    Decision Node — Make final workflow decision.

    Reads: intent, extracted_entities, retrieved_context, risk_analysis, llm_provider
    Writes: decision
    """
    logger.info("━━━ Node: Decision Agent ━━━")
    agent = DecisionAgent()

    try:
        result = agent.process(
            intent=state.get("intent"),
            extracted_entities=state.get("extracted_entities"),
            retrieved_context=state.get("retrieved_context", []),
            risk_analysis=state.get("risk_analysis"),
            llm_provider=state.get("llm_provider"),
            api_key=state.get("api_key"),
        )
        return {"decision": result}
    except Exception as e:
        clean_err = _clean_error(e)
        logger.error(f"Decision node failed: {e}")
        errors = list(state.get("errors", []))
        errors.append(f"Decision making failed: {clean_err}")
        return {
            "decision": {
                "decision": "flag_for_manual_review",
                "confidence": 0.0,
                "reasoning": f"Decision error: {clean_err}",
                "priority": "medium",
            },
            "errors": errors,
        }


def action_node(state: WorkflowState) -> dict:
    """
    Action Node — Execute business actions based on decision.

    Reads: decision, intent, extracted_entities, risk_analysis, document_id
    Writes: actions
    """
    logger.info("━━━ Node: Action Agent ━━━")
    agent = ActionAgent()

    try:
        result = agent.process(
            decision=state.get("decision"),
            intent=state.get("intent"),
            extracted_entities=state.get("extracted_entities"),
            risk_analysis=state.get("risk_analysis"),
            document_id=state.get("document_id", ""),
        )
        return {"actions": result.get("actions", [])}
    except Exception as e:
        clean_err = _clean_error(e)
        logger.error(f"Action node failed: {e}")
        errors = list(state.get("errors", []))
        errors.append(f"Action execution failed: {clean_err}")
        return {
            "actions": [{
                "action_type": "error",
                "status": "failed",
                "details": {"error": clean_err},
                "timestamp": "",
            }],
            "errors": errors,
        }
