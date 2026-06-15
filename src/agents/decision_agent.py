"""
Decision Agent — Intelligent workflow decision making using LLM.

Reasons over all accumulated data (intent, entities, knowledge, risk)
to produce a final workflow decision with confidence and reasoning.
"""

import json

from langchain_core.messages import HumanMessage, SystemMessage

from src.core.llm_factory import LLMFactory
from src.core.logging import get_logger
from src.schemas.agent_outputs import WorkflowDecision

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are an expert decision-making agent for a business document intelligence platform.

Your task is to analyze all available information about a processed document and make a
final workflow decision about what action should be taken.

Available decisions:
- "escalate_to_crm": Create a high-priority CRM ticket (for urgent complaints, threats, critical issues)
- "create_support_ticket": Create a standard support ticket (for support requests, general issues)
- "flag_for_compliance_review": Flag for compliance team review (for regulatory documents)
- "escalate_fraud_alert": Escalate to fraud team (for high-risk fraud indicators)
- "review_high_value_invoice": Route to finance for review (for high-value invoices)
- "process_standard_invoice": Standard invoice processing (for normal invoices)
- "send_rfq_response": Generate and send RFQ response (for quotation requests)
- "flag_for_manual_review": Flag for human review (when automated processing is insufficient)
- "log_and_close": Log the document and close (for informational items, low-priority)
- "request_clarification": Request additional information (for ambiguous or incomplete documents)

Decision Guidelines:
1. High risk score (>0.5) → Prefer escalation or manual review
2. Complaint + High urgency → escalate_to_crm
3. Fraud indicators → escalate_fraud_alert
4. Compliance keywords → flag_for_compliance_review
5. Invoice > $50,000 → review_high_value_invoice
6. Low risk + clear intent → process automatically
7. Ambiguous content → flag_for_manual_review or request_clarification

Provide clear reasoning for your decision and an appropriate priority level."""


class DecisionAgent:
    """
    Makes final workflow decisions using LLM reasoning.

    Takes all accumulated workflow data and produces a structured
    WorkflowDecision with decision type, confidence, reasoning, and priority.
    """

    def process(
        self,
        intent: dict | None,
        extracted_entities: dict | None,
        retrieved_context: list[str],
        risk_analysis: dict | None,
        llm_provider: str | None = None,
    ) -> dict:
        """
        Make a workflow decision based on all accumulated data.

        Args:
            intent: Intent classification dict.
            extracted_entities: Extracted entities dict.
            retrieved_context: Retrieved knowledge context.
            risk_analysis: Risk analysis dict.
            llm_provider: Optional LLM provider override.

        Returns:
            WorkflowDecision as a dict.
        """
        logger.info("[DecisionAgent] Making workflow decision")

        try:
            llm = LLMFactory.create(provider=llm_provider, temperature=0.2)
            structured_llm = llm.with_structured_output(WorkflowDecision)

            # Build comprehensive context
            analysis_summary = self._build_summary(
                intent, extracted_entities, retrieved_context, risk_analysis
            )

            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=(
                    f"Based on the following document analysis, "
                    f"make a workflow decision:\n\n{analysis_summary}"
                )),
            ]

            result: WorkflowDecision = structured_llm.invoke(messages)

            logger.info(
                f"[DecisionAgent] Decision: {result.decision}, "
                f"confidence={result.confidence:.2f}, priority={result.priority}"
            )

            return result.model_dump()

        except Exception as e:
            logger.error(f"[DecisionAgent] Decision failed: {e}")
            return WorkflowDecision(
                decision="flag_for_manual_review",
                confidence=0.0,
                reasoning=f"Automated decision failed: {e}. Manual review required.",
                priority="medium",
            ).model_dump()

    def _build_summary(
        self,
        intent: dict | None,
        extracted_entities: dict | None,
        retrieved_context: list[str],
        risk_analysis: dict | None,
    ) -> str:
        """Build a comprehensive analysis summary for the decision LLM."""
        sections = []

        if intent:
            sections.append(
                f"## Intent Classification\n"
                f"- Intent: {intent.get('intent', 'unknown')}\n"
                f"- Confidence: {intent.get('confidence', 0):.2f}\n"
                f"- Reasoning: {intent.get('reasoning', 'N/A')}"
            )

        if extracted_entities:
            entities = extracted_entities.get("entities", {})
            entities_str = json.dumps(entities, indent=2, default=str)
            sections.append(
                f"## Extracted Entities ({extracted_entities.get('entity_type', 'unknown')})\n"
                f"```json\n{entities_str}\n```"
            )

        if risk_analysis:
            sections.append(
                f"## Risk Analysis\n"
                f"- Risk Score: {risk_analysis.get('risk_score', 0):.2f}\n"
                f"- Risk Level: {risk_analysis.get('risk_level', 'unknown')}\n"
                f"- Risk Factors: {', '.join(risk_analysis.get('risk_factors', []))}\n"
                f"- Recommended Action: {risk_analysis.get('recommended_action', 'N/A')}"
            )

        if retrieved_context:
            context_preview = "\n".join(
                f"- {chunk[:200]}..." for chunk in retrieved_context[:3]
            )
            sections.append(
                f"## Retrieved Business Knowledge\n{context_preview}"
            )

        return "\n\n".join(sections) if sections else "No analysis data available."
