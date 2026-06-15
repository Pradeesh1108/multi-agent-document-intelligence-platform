"""
Extraction Agent — Intent-aware structured entity extraction.

Extracts entities using different Pydantic schemas based on the
classified intent. Uses LLM with structured output for type-safe extraction.
"""

from langchain_core.messages import HumanMessage, SystemMessage

from src.core.llm_factory import LLMFactory
from src.core.logging import get_logger
from src.schemas.agent_outputs import (
    ComplaintEntities,
    ExtractedEntities,
    GenericEntities,
    InvoiceEntities,
    PDFEntities,
    RFQEntities,
)

logger = get_logger(__name__)

# Maps intents to their extraction schemas
INTENT_SCHEMA_MAP = {
    "invoice": InvoiceEntities,
    "complaint": ComplaintEntities,
    "rfq": RFQEntities,
    "compliance": PDFEntities,
    "fraud_risk": GenericEntities,
    "support_request": ComplaintEntities,
    "general_inquiry": GenericEntities,
    "other": GenericEntities,
}

SYSTEM_PROMPT = """You are an expert entity extraction agent for a business document processing platform.

Your task is to carefully extract structured entities from the provided document content.
Extract all relevant fields based on the document's intent. Be thorough but accurate.

Guidelines:
- Extract only information that is explicitly stated or strongly implied in the document
- Use null/None for fields that cannot be determined from the content
- For monetary amounts, extract the numeric value only
- For dates, use the format as found in the document
- Provide a brief, accurate summary when required
- Be precise with names, emails, and identifiers — copy them exactly as found"""


class ExtractionAgent:
    """
    Extracts structured entities using intent-aware schemas.

    Selects the appropriate Pydantic schema based on the classified
    intent, then uses LLM with_structured_output() for extraction.
    """

    def process(
        self,
        normalized_content: str,
        intent: str,
        file_type: str,
        llm_provider: str | None = None,
    ) -> dict:
        """
        Extract entities from document content.

        Args:
            normalized_content: Preprocessed document text.
            intent: Classified document intent.
            file_type: Document file type.
            llm_provider: Optional LLM provider override.

        Returns:
            ExtractedEntities as a dict.
        """
        logger.info(f"[ExtractionAgent] Extracting entities (intent: {intent})")

        # Select the appropriate schema
        schema_class = INTENT_SCHEMA_MAP.get(intent, GenericEntities)
        schema_name = schema_class.__name__

        try:
            llm = LLMFactory.create(provider=llm_provider, temperature=0.1)
            structured_llm = llm.with_structured_output(schema_class)

            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=(
                    f"Document intent: {intent}\n"
                    f"Document type: {file_type}\n"
                    f"Extraction schema: {schema_name}\n\n"
                    f"Document content:\n{normalized_content[:4000]}"
                )),
            ]

            result = structured_llm.invoke(messages)
            entities_dict = result.model_dump()

            logger.info(
                f"[ExtractionAgent] Extracted {len(entities_dict)} fields "
                f"using {schema_name}"
            )

            return ExtractedEntities(
                entity_type=intent,
                entities=entities_dict,
                confidence=0.85,
            ).model_dump()

        except Exception as e:
            logger.error(f"[ExtractionAgent] Extraction failed: {e}")
            return ExtractedEntities(
                entity_type=intent,
                entities={"error": str(e), "raw_content_preview": normalized_content[:500]},
                confidence=0.0,
            ).model_dump()
