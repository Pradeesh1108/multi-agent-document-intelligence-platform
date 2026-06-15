"""
Document processing routes.
"""

import os
import shutil
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from src.core.config import get_settings
from src.core.logging import get_logger
from src.schemas.workflow import WorkflowResult
from src.services.workflow_service import WorkflowService

logger = get_logger(__name__)
router = APIRouter(prefix="/documents", tags=["Documents"])

# Singleton workflow service
_workflow_service: Optional[WorkflowService] = None


def get_workflow_service() -> WorkflowService:
    """Get or create the workflow service singleton."""
    global _workflow_service
    if _workflow_service is None:
        _workflow_service = WorkflowService()
    return _workflow_service


@router.post("/process", response_model=WorkflowResult)
async def process_document(
    file: UploadFile = File(None),
    raw_text_input: Optional[str] = Form(None),
    llm_provider: Optional[str] = Form(None),
) -> WorkflowResult:
    """
    Process a document through the multi-agent workflow.

    Accepts either a file upload OR raw text input.
    Optionally override the LLM provider for this request.
    """
    service = get_workflow_service()

    if file and file.filename:
        return await _process_file(service, file, llm_provider)
    elif raw_text_input:
        return await _process_text(service, raw_text_input, llm_provider)
    else:
        raise HTTPException(
            status_code=400,
            detail="No input provided. Please provide either a file or raw_text_input.",
        )


@router.post("/upload", response_model=WorkflowResult)
async def upload_document(
    file: UploadFile = File(...),
    llm_provider: Optional[str] = Form(None),
) -> WorkflowResult:
    """
    Upload and process a document file.

    Supported formats: .pdf, .json, .txt, .eml
    """
    service = get_workflow_service()
    return await _process_file(service, file, llm_provider)


async def _process_file(
    service: WorkflowService,
    file: UploadFile,
    llm_provider: str | None,
) -> WorkflowResult:
    """Handle file upload processing."""
    settings = get_settings()

    # Validate file extension
    filename = file.filename or "unknown"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ("pdf", "json", "txt", "eml"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{ext}'. Supported: .pdf, .json, .txt, .eml",
        )

    # Save file temporarily
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File saved temporarily: {file_path}")

        # Process
        result = await service.process_file(file_path, filename, llm_provider)
        return result

    finally:
        # Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Temp file cleaned up: {file_path}")


async def _process_text(
    service: WorkflowService,
    raw_text: str,
    llm_provider: str | None,
) -> WorkflowResult:
    """Handle raw text processing."""
    if not raw_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Input text is empty.",
        )

    logger.info(f"Processing raw text input ({len(raw_text)} chars)")
    return await service.process_text(raw_text, llm_provider)
