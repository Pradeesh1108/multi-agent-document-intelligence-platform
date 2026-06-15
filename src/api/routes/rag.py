"""
RAG ingestion route.
"""

from fastapi import APIRouter

from src.core.logging import get_logger
from src.rag.ingestion import ingest
from src.schemas.workflow import RAGIngestRequest

logger = get_logger(__name__)
router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/ingest")
async def ingest_knowledge_base(request: RAGIngestRequest = RAGIngestRequest()) -> dict:
    """
    Trigger knowledge base ingestion.

    Reads documents from the knowledge_base/ directory,
    chunks them, and stores in ChromaDB.
    """
    logger.info("RAG ingestion triggered via API")

    try:
        total_chunks = ingest()
        return {
            "status": "success",
            "message": f"Ingested {total_chunks} chunks into knowledge base",
            "total_chunks": total_chunks,
        }
    except Exception as e:
        logger.error(f"RAG ingestion failed: {e}")
        return {
            "status": "error",
            "message": f"Ingestion failed: {e}",
            "total_chunks": 0,
        }
