"""
Risk Agent — Document risk analysis using LLM.

Analyzes documents for fraud indicators, missing information,
compliance concerns, and other risk factors.
"""

import json

from langchain_core.messages import HumanMessage, SystemMessage

from src.core.llm_factory import LLMFactory
from src.core.logging import get_logger
from src.schemas.agent_outputs import RiskAnalysis

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are an expert risk analysis agent for a business document processing platform.

Your task is to assess the risk level of a processed document based on:
1. The document's intent classification
2. Extracted entities and their values
3. Any retrieved business knowledge/policies
4. General risk indicators

Risk Assessment Guidelines:

FRAUD INDICATORS:
- Unusually high monetary amounts
- Transactions from high-risk regions
- Missing critical identification fields
- Inconsistent data (e.g., mismatched dates, amounts)
- New or unknown entities requesting large transactions

COMPLIANCE CONCERNS:
- Documents referencing regulated data (PII, PHI, financial records)
- Missing required regulatory disclosures
- Cross-border data handling without proper documentation
- Regulatory keywords (GDPR, HIPAA, SOX, PCI DSS) without compliance review

MISSING INFORMATION:
- Critical fields not found in extraction
- Ambiguous or incomplete data
- No verifiable contact information

GENERAL RISK:
- Threatening language or tone
- Legal implications mentioned
- Time-sensitive demands with unreasonable deadlines

Scoring:
- 0.0-0.2: Low risk — Standard processing
- 0.2-0.5: Medium risk — Enhanced monitoring recommended
- 0.5-0.7: High risk — Manual review required
- 0.7-1.0: Critical risk — Immediate escalation required

Always provide specific risk factors and a clear explanation."""


class RiskAgent:
    """
    Analyzes document risk using LLM with structured output.

    Produces a validated RiskAnalysis object with score, level,
    factors, and recommended action.
    """

    def process(
        self,
        normalized_content: str,
        intent: dict | None,
        extracted_entities: dict | None,
        retrieved_context: list[str],
        llm_provider: str | None = None,
    ) -> dict:
        """
        Analyze document risk.

        Args:
            normalized_content: Preprocessed document text.
            intent: Intent classification dict.
            extracted_entities: Extracted entities dict.
            retrieved_context: Retrieved knowledge context.
            llm_provider: Optional LLM provider override.

        Returns:
            RiskAnalysis as a dict.
        """
        logger.info("[RiskAgent] Performing risk analysis")

        try:
            llm = LLMFactory.create(provider=llm_provider, temperature=0.1)
            structured_llm = llm.with_structured_output(RiskAnalysis)

            # Build context for risk analysis
            context_parts = []

            if intent:
                context_parts.append(f"Intent: {intent.get('intent', 'unknown')} "
                                     f"(confidence: {intent.get('confidence', 0):.2f})")

            if extracted_entities:
                entities_str = json.dumps(
                    extracted_entities.get("entities", {}),
                    indent=2, default=str,
                )
                context_parts.append(f"Extracted Entities:\n{entities_str}")

            if retrieved_context:
                context_parts.append(
                    "Relevant Business Policies:\n" +
                    "\n---\n".join(retrieved_context[:3])
                )

            context_block = "\n\n".join(context_parts)

            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=(
                    f"Analyze the risk for the following document:\n\n"
                    f"--- Analysis Context ---\n{context_block}\n\n"
                    f"--- Document Content ---\n{normalized_content[:3000]}"
                )),
            ]

            result: RiskAnalysis = structured_llm.invoke(messages)

            logger.info(
                f"[RiskAgent] Risk assessed: score={result.risk_score:.2f}, "
                f"level={result.risk_level}, factors={len(result.risk_factors)}"
            )

            return result.model_dump()

        except Exception as e:
            logger.error(f"[RiskAgent] Risk analysis failed: {e}")
            return RiskAnalysis(
                risk_score=0.5,
                risk_level="medium",
                risk_factors=[f"Risk analysis error: {e}"],
                recommended_action="Manual review recommended due to analysis failure",
                explanation=f"Risk analysis could not be completed: {e}",
            ).model_dump()
