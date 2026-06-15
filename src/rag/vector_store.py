"""
Vector Store — ChromaDB wrapper for knowledge base storage and retrieval.

Manages the ChromaDB client, collection creation, and embedding configuration.
"""

from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)

# Module-level singleton for the ChromaDB client
_chroma_client: Optional[chromadb.ClientAPI] = None
_collection_name: str = "knowledge_base"


def get_chroma_client() -> chromadb.ClientAPI:
    """
    Get or create the ChromaDB persistent client singleton.

    Returns:
        Configured ChromaDB client with persistent storage.
    """
    global _chroma_client
    if _chroma_client is None:
        settings = get_settings()
        logger.info(f"Initializing ChromaDB client at: {settings.CHROMA_PERSIST_DIR}")
        _chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _chroma_client


def get_or_create_collection(
    collection_name: str = _collection_name,
) -> chromadb.Collection:
    """
    Get or create a ChromaDB collection.

    Args:
        collection_name: Name of the collection.

    Returns:
        ChromaDB collection instance.
    """
    client = get_chroma_client()
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    logger.info(
        f"ChromaDB collection '{collection_name}' ready "
        f"(documents: {collection.count()})"
    )
    return collection


def collection_exists(collection_name: str = _collection_name) -> bool:
    """Check if a collection exists and has documents."""
    try:
        client = get_chroma_client()
        collection = client.get_collection(name=collection_name)
        return collection.count() > 0
    except Exception:
        return False
