"""
Intent Agent — Document intent classification using LLM.

Classifies documents into business intents using structured output
from the LLM, eliminating manual JSON parsing.
"""

from langchain_core.messages import HumanMessage, SystemMessage

from src.core.llm_factory import LLMFactory
from src.core.logging import get_logger
from src.core.utils import clean_llm_error
from src.schemas.agent_outputs import IntentClassification

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are an expert document classification agent for a business intelligence platform.

Your task is to analyze the provided document content and classify its primary business intent.

Available intents:
- "complaint": Customer complaints, dissatisfaction, service issues
- "invoice": Invoices, bills, payment requests, financial documents
- "rfq": Requests for quotation, pricing inquiries, procurement requests
- "compliance": Regulatory documents, policy documents, compliance-related content
- "fraud_risk": Suspicious activities, fraud indicators (e.g., unexpected bank account changes, urgent wire transfers), security threats
- "support_request": Technical support requests, help requests, bug reports
- "general_inquiry": General questions, information requests, follow-ups
- "other": Content that doesn't clearly fit any category above

Classify the intent based on the overall meaning and purpose of the document.
Provide a confidence score (0.0 to 1.0) and a brief reasoning for your classification.

Be precise. If the document clearly matches a specific intent, assign high confidence (>0.8).
If ambiguous, choose the most likely intent and indicate uncertainty with a lower confidence score."""


class IntentAgent:
    """
    Classifies document intent using LLM with structured output.

    Uses LangChain's with_structured_output() to produce validated
    IntentClassification objects directly from the LLM.
    """

    def process(
        self,
        normalized_content: str,
        file_type: str,
        llm_provider: str | None = None,
        api_key: str | None = None,
    ) -> dict:
        """
        Classify the intent of the document.

        Args:
            normalized_content: Preprocessed document text.
            file_type: Detected file type for additional context.
            llm_provider: Optional LLM provider override.

        Returns:
            IntentClassification as a dict.
        """
        logger.info(f"[IntentAgent] Classifying intent (type: {file_type})")

        try:
            llm = LLMFactory.create(provider=llm_provider, api_key=api_key, temperature=0.1)
            structured_llm = llm.with_structured_output(IntentClassification)

            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=(
                    f"Document type: {file_type}\n\n"
                    f"Document content:\n{normalized_content[:4000]}"
                )),
            ]

            result: IntentClassification = structured_llm.invoke(messages)

            logger.info(
                f"[IntentAgent] Classified: intent={result.intent}, "
                f"confidence={result.confidence:.2f}"
            )

            return result.model_dump()

        except Exception as e:
            clean_err = clean_llm_error(e)
            logger.error(f"[IntentAgent] Classification failed: {e}")
            # Return a safe fallback
            return IntentClassification(
                intent="other",
                confidence=0.0,
                reasoning=clean_err,
            ).model_dump()
