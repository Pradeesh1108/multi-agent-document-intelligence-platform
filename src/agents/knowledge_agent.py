"""
Knowledge Agent — RAG-based knowledge retrieval.

Queries the ChromaDB knowledge base for relevant business context.
Designed for graceful degradation — never blocks the workflow.
"""

from src.core.logging import get_logger
from src.rag.retriever import KnowledgeRetriever

logger = get_logger(__name__)


class KnowledgeAgent:
    """
    Retrieves relevant business knowledge from the vector store.

    If the knowledge base is empty or retrieval fails, the agent
    returns empty context gracefully without blocking the workflow.
    """

    def __init__(self) -> None:
        self._retriever = KnowledgeRetriever(n_results=3)

    def process(
        self,
        normalized_content: str,
        intent: str,
    ) -> dict:
        """
        Retrieve relevant knowledge for the document.

        Args:
            normalized_content: Document content for semantic search.
            intent: Classified intent to help focus retrieval.

        Returns:
            Dict with retrieved_context list.
        """
        logger.info(f"[KnowledgeAgent] Retrieving context (intent: {intent})")

        # Build a focused query combining intent and content
        query = self._build_query(normalized_content, intent)

        # Retrieve from knowledge base
        context_chunks = self._retriever.retrieve(query)

        if context_chunks:
            logger.info(
                f"[KnowledgeAgent] Retrieved {len(context_chunks)} "
                f"knowledge chunks for intent '{intent}'"
            )
        else:
            logger.info(
                f"[KnowledgeAgent] No knowledge context available "
                f"for intent '{intent}'. Continuing without context."
            )

        return {
            "retrieved_context": context_chunks,
        }

    def _build_query(self, content: str, intent: str) -> str:
        """
        Build a focused search query for knowledge retrieval.

        Combines the intent with a snippet of the document content
        to produce a more targeted semantic search.
        """
        intent_context = {
            "complaint": "customer complaint handling escalation policy",
            "invoice": "invoice processing validation financial guidelines",
            "rfq": "request for quotation procurement process",
            "compliance": "regulatory compliance GDPR HIPAA requirements",
            "fraud_risk": "fraud detection risk assessment rules",
            "support_request": "technical support resolution process",
            "general_inquiry": "general business procedures",
            "other": "document processing guidelines",
        }

        intent_prefix = intent_context.get(intent, "business document processing")
        content_snippet = content[:300]

        return f"{intent_prefix}: {content_snippet}"
