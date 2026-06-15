"""
Workflow management routes.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException

from src.core.logging import get_logger
from src.schemas.workflow import ProcessDocumentRequest, WorkflowResult
from src.services.workflow_service import WorkflowService

logger = get_logger(__name__)
router = APIRouter(prefix="/workflow", tags=["Workflow"])

# Singleton workflow service
_workflow_service: Optional[WorkflowService] = None


def get_workflow_service() -> WorkflowService:
    """Get or create the workflow service singleton."""
    global _workflow_service
    if _workflow_service is None:
        _workflow_service = WorkflowService()
    return _workflow_service


@router.post("/run", response_model=WorkflowResult)
async def run_workflow(request: ProcessDocumentRequest) -> WorkflowResult:
    """
    Run the document processing workflow with a JSON request body.

    This endpoint accepts a JSON body (unlike /documents/process which
    uses multipart form data).
    """
    service = get_workflow_service()

    if not request.raw_text_input or not request.raw_text_input.strip():
        raise HTTPException(
            status_code=400,
            detail="raw_text_input is required and cannot be empty.",
        )

    logger.info(
        f"Running workflow via /workflow/run "
        f"(provider: {request.llm_provider or 'default'})"
    )

    return await service.process_text(
        raw_text=request.raw_text_input,
        llm_provider=request.llm_provider,
    )


@router.get("/status/{workflow_id}")
async def get_workflow_status(workflow_id: str) -> dict:
    """
    Get the status of a workflow execution.

    Returns the current status, timing, and any errors.
    """
    service = get_workflow_service()
    status = service.get_workflow_status(workflow_id)

    if status is None:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow '{workflow_id}' not found.",
        )

    return {
        "workflow_id": workflow_id,
        **status,
    }
