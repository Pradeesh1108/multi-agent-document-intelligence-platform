"""
RAG Retriever — Retrieves relevant knowledge from ChromaDB.

Provides a simple interface for the Knowledge Agent to query
the vector store for contextually relevant business knowledge.
"""

from src.core.logging import get_logger
from src.rag.vector_store import collection_exists, get_or_create_collection

logger = get_logger(__name__)


class KnowledgeRetriever:
    """
    Retrieves relevant context from the ChromaDB knowledge base.

    Designed for graceful degradation — if the knowledge base is empty
    or retrieval fails, returns an empty list instead of raising errors.
    """

    def __init__(self, collection_name: str = "knowledge_base", n_results: int = 3):
        """
        Initialize the retriever.

        Args:
            collection_name: ChromaDB collection to query.
            n_results: Number of results to retrieve per query.
        """
        self.collection_name = collection_name
        self.n_results = n_results

    def retrieve(self, query: str) -> list[str]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: The search query text.

        Returns:
            List of relevant document text chunks. Empty list if
            no knowledge base exists or retrieval fails.
        """
        if not query.strip():
            logger.warning("Empty query provided to retriever")
            return []

        if not collection_exists(self.collection_name):
            logger.info(
                f"Knowledge base collection '{self.collection_name}' is empty or "
                f"does not exist. Continuing without retrieved context."
            )
            return []

        try:
            collection = get_or_create_collection(self.collection_name)
            results = collection.query(
                query_texts=[query],
                n_results=min(self.n_results, collection.count()),
            )

            documents = results.get("documents", [[]])[0]
            distances = results.get("distances", [[]])[0]

            # Log retrieval results
            if documents:
                logger.info(
                    f"Retrieved {len(documents)} relevant chunks "
                    f"(best distance: {distances[0]:.4f})"
                )
            else:
                logger.info("No relevant documents found in knowledge base")

            return documents

        except Exception as e:
            logger.warning(
                f"Knowledge retrieval failed (non-blocking): {e}. "
                f"Continuing without retrieved context."
            )
            return []
