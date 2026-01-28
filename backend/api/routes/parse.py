"""Parse API routes."""
from fastapi import APIRouter, HTTPException, Response, status

from api.schemas.parse_result import ParseRequest, ParseResponse
from api.schemas.job import JobResponse
from application.services.parser_service import ParserService
from application.services.job_service import JobService
from core.models.job import JobStatus
from api.routes.documents import document_service
from infrastructure.queue.redis_queue import default_queue
from application.workers.parse_worker import parse_document_task
from core.models.parse_result import ParseResult

router = APIRouter()
parser_service = ParserService()

# Shared JobService instance (same as in jobs.py)
# Note: In production, this should be a proper singleton or dependency injection
_job_service_instance = None

def get_job_service() -> JobService:
    """Get shared JobService instance."""
    global _job_service_instance
    if _job_service_instance is None:
        _job_service_instance = JobService()
    return _job_service_instance

job_service = get_job_service()


@router.post("/documents/{document_id}/pages/{page_number}/parse", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def parse_document(
    document_id: str,
    page_number: int,
    request: ParseRequest = ParseRequest()
):
    """Parse a document asynchronously.
    
    Args:
        document_id: Document ID
        page_number: Page number (0-indexed)
        request: Parse request with mode ('basic' or 'enhance')
        
    Returns:
        JobResponse with job_id (202 Accepted)
        
    Note:
        - Returns immediately with job_id
        - Use GET /jobs/{job_id} to poll for status
        - Parse result available via GET /parse/result after completion
    """
    # Get document
    document = document_service.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Validate page number
    if page_number < 0:
        raise HTTPException(status_code=400, detail="Page number must be >= 0")
    if page_number >= document.page_count:
        raise HTTPException(
            status_code=404,
            detail=f"Page {page_number} not found. Document has {document.page_count} page(s)"
        )
    
    # Validate mode
    if request.mode not in ["basic", "enhance"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode: {request.mode}. Use 'basic' or 'enhance'"
        )
    
    # Create job
    try:
        job = job_service.create_job(document_id, page_number, request.mode)
        
        # Queue task
        default_queue.enqueue(
            parse_document_task,
            job.id,
            document_id,
            page_number,
            request.mode,
            job_timeout=360  # 6 minutes
        )
        
        # Update job status to queued
        job_service.update_job_status(job.id, JobStatus.QUEUED)
        
        # Return job_id immediately
        return JobResponse.from_domain(job)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue parsing job: {str(e)}"
        )


@router.get("/documents/{document_id}/pages/{page_number}/parse/result")
async def get_parse_result(
    document_id: str,
    page_number: int,
    format: str = "blocks",
    mode: str = "basic"
):
    """Get parse result in different formats.
    
    Args:
        document_id: Document ID
        page_number: Page number (0-indexed)
        format: Output format (blocks, json, html, markdown)
        mode: Parse mode ('basic' or 'enhance') - required to retrieve cached result
        
    Returns:
        Parse result in requested format
        
    Note:
        - Retrieves cached parse result from DocumentService
        - If not cached, returns 404 (user must parse first)
    """
    # Get document
    document = document_service.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Validate page number
    if page_number < 0:
        raise HTTPException(status_code=400, detail="Page number must be >= 0")
    if page_number >= document.page_count:
        raise HTTPException(
            status_code=404,
            detail=f"Page {page_number} not found. Document has {document.page_count} page(s)"
        )
    
    # Validate format
    if format not in ["blocks", "json", "html", "markdown"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format: {format}. Use 'blocks', 'json', 'html', or 'markdown'"
        )
    
    # Validate mode
    if mode not in ["basic", "enhance"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode: {mode}. Use 'basic' or 'enhance'"
        )
    
    # Get cached parse result
    parse_result = document_service.get_parse_result(document_id, page_number, mode)
    if not parse_result:
        raise HTTPException(
            status_code=404,
            detail=f"Parse result not found. Please parse the document first using POST /documents/{document_id}/pages/{page_number}/parse"
        )
    
    # Return in requested format
    if format == "blocks":
        return ParseResponse.from_domain(parse_result)
    elif format == "json":
        # FastAPI automatically converts dict to JSON
        return parse_result.to_dict()
    elif format == "html":
        return Response(
            content=parse_result.to_html(),
            media_type="text/html"
        )
    elif format == "markdown":
        return Response(
            content=parse_result.to_markdown(),
            media_type="text/markdown"
        )


@router.get("/parsers")
async def list_parsers():
    """List available parsers and modes.
    
    Returns:
        List of available parser names and modes
    """
    parsers = parser_service.get_available_parsers()
    modes = parser_service.get_available_modes()
    
    return {
        "parsers": parsers,
        "modes": modes,
        "mode_mapping": {
            "basic": "docling",
            "enhance": "chandra",
        }
    }
