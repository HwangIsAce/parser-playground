"""RQ worker tasks for document parsing."""
from rq import get_current_job

from core.models.job import JobStatus
from application.services.parser_service import ParserService
from application.services.document_service import DocumentService
from application.services.job_service import JobService

# Services (singleton instances)
# Note: These are created per worker process
parser_service = ParserService()
document_service = DocumentService()
job_service = JobService()


def parse_document_task(
    job_id: str,
    document_id: str,
    page_number: int,
    mode: str
) -> dict:
    """RQ task for parsing a document.
    
    Args:
        job_id: Job ID
        document_id: Document ID
        page_number: Page number (0-indexed)
        mode: Parse mode ('basic' or 'enhance')
        
    Returns:
        Dict with parse result data
        
    Note:
        - Updates job status during processing
        - Saves parse result to cache
    """
    # Get current RQ job for progress tracking (optional)
    rq_job = get_current_job()
    
    try:
        # Update job status to processing
        job_service.update_job_status(job_id, JobStatus.PROCESSING)
        
        # Get document
        document = document_service.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document not found: {document_id}")
        
        # Parse document
        parse_result = parser_service.parse_document(document, mode=mode)
        
        # Save parse result to cache
        document_service.save_parse_result(
            document_id,
            page_number,
            mode,
            parse_result
        )
        
        # Update job status to completed
        job_service.update_job_status(
            job_id,
            JobStatus.COMPLETED,
            result=parse_result
        )
        
        # Return result for RQ
        return {
            "status": "completed",
            "document_id": document_id,
            "parse_result": parse_result.to_dict()
        }
        
    except Exception as e:
        # Update job status to failed
        job_service.update_job_status(
            job_id,
            JobStatus.FAILED,
            error=str(e)
        )
        raise  # Re-raise for RQ error handling
