"""
RAG Ingestion Pipeline — Loads, chunks, and stores knowledge base documents.

Reads documents from the knowledge_base/ directory, splits them into chunks,
and stores them in ChromaDB for retrieval.

Usage (standalone):
    uv run python -m src.rag.ingestion
"""

import os
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.logging import get_logger, setup_logging
from src.rag.vector_store import get_or_create_collection

logger = get_logger(__name__)

# Knowledge base root directory (relative to project root)
KNOWLEDGE_BASE_DIR = Path("knowledge_base")


def load_documents(base_dir: Path | None = None) -> list[dict[str, str]]:
    """
    Load all text/markdown documents from the knowledge base directory.

    Args:
        base_dir: Root directory of the knowledge base.
                  Defaults to KNOWLEDGE_BASE_DIR.

    Returns:
        List of dicts with 'content', 'source', and 'category' keys.
    """
    base_dir = base_dir or KNOWLEDGE_BASE_DIR
    documents: list[dict[str, str]] = []

    if not base_dir.exists():
        logger.warning(f"Knowledge base directory not found: {base_dir}")
        return documents

    supported_extensions = {".md", ".txt", ".text"}

    for root, _dirs, files in os.walk(base_dir):
        for filename in sorted(files):
            filepath = Path(root) / filename
            if filepath.suffix.lower() not in supported_extensions:
                continue

            try:
                content = filepath.read_text(encoding="utf-8")
                # Determine category from subdirectory name
                relative = filepath.relative_to(base_dir)
                category = relative.parts[0] if len(relative.parts) > 1 else "general"

                documents.append({
                    "content": content,
                    "source": str(relative),
                    "category": category,
                })
                logger.info(f"  Loaded: {relative} ({len(content)} chars, category: {category})")
            except Exception as e:
                logger.error(f"  Failed to load {filepath}: {e}")

    logger.info(f"Loaded {len(documents)} documents from knowledge base")
    return documents


def chunk_documents(
    documents: list[dict[str, str]],
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> tuple[list[str], list[dict[str, str]], list[str]]:
    """
    Split documents into chunks for vector storage.

    Args:
        documents: List of document dicts from load_documents().
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlap between consecutive chunks.

    Returns:
        Tuple of (texts, metadatas, ids) ready for ChromaDB insertion.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    all_texts: list[str] = []
    all_metadatas: list[dict[str, str]] = []
    all_ids: list[str] = []

    for doc in documents:
        chunks = splitter.split_text(doc["content"])
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc['source']}::chunk_{i}"
            all_texts.append(chunk)
            all_metadatas.append({
                "source": doc["source"],
                "category": doc["category"],
                "chunk_index": str(i),
            })
            all_ids.append(chunk_id)

    logger.info(f"Created {len(all_texts)} chunks from {len(documents)} documents")
    return all_texts, all_metadatas, all_ids


def ingest(base_dir: Path | None = None) -> int:
    """
    Run the full ingestion pipeline: load → chunk → store.

    Args:
        base_dir: Knowledge base directory. Defaults to KNOWLEDGE_BASE_DIR.

    Returns:
        Number of chunks ingested.
    """
    logger.info("=" * 60)
    logger.info("Starting Knowledge Base Ingestion Pipeline")
    logger.info("=" * 60)

    # Load documents
    documents = load_documents(base_dir)
    if not documents:
        logger.warning("No documents found to ingest. Exiting.")
        return 0

    # Chunk documents
    texts, metadatas, ids = chunk_documents(documents)
    if not texts:
        logger.warning("No chunks generated. Exiting.")
        return 0

    # Store in ChromaDB
    collection = get_or_create_collection()

    # Upsert in batches to handle large knowledge bases
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch_end = min(i + batch_size, len(texts))
        collection.upsert(
            documents=texts[i:batch_end],
            metadatas=metadatas[i:batch_end],
            ids=ids[i:batch_end],
        )
        logger.info(f"  Upserted batch {i // batch_size + 1}: chunks {i+1}-{batch_end}")

    total = collection.count()
    logger.info("=" * 60)
    logger.info(f"Ingestion complete! Total chunks in knowledge base: {total}")
    logger.info("=" * 60)
    return total


if __name__ == "__main__":
    setup_logging("INFO")
    ingest()
