"""Parse API routes."""
from fastapi import APIRouter, HTTPException

from api.schemas.parse_result import ParseRequest, ParseResponse
from application.services.parser_service import ParserService
from application.services.document_service import DocumentService

router = APIRouter()
parser_service = ParserService()
document_service = DocumentService()


@router.post("/documents/{document_id}/pages/{page_number}/parse", response_model=ParseResponse)
async def parse_document(document_id: str, page_number: int, request: ParseRequest = ParseRequest()):
    """Parse a specific page of the document.
    
    Args:
        document_id: Document ID
        page_number: Page number (0-indexed)
        request: Parse request with optional parser name
        
    Returns:
        ParseResponse with parsed data
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
    
    # Parse document
    try:
        parse_result = parser_service.parse_document(
            document,
            parser_name=request.parser_name
        )
        return ParseResponse.from_domain(parse_result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse document: {str(e)}"
        )


@router.get("/documents/{document_id}/pages/{page_number}/parse/result")
async def get_parse_result(document_id: str, page_number: int, format: str = "blocks"):
    """Get parse result in different formats.
    
    Args:
        document_id: Document ID
        page_number: Page number (0-indexed)
        format: Output format (blocks, json, html, markdown)
        
    Returns:
        Parse result in requested format
        
    Note:
        Future: Can retrieve cached results from database
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
    
    # TODO: Retrieve parse result from cache/database
    # For now, return error
    raise HTTPException(
        status_code=501,
        detail="Parse result retrieval not implemented yet. "
               "Please use POST /documents/{document_id}/pages/{page_number}/parse to parse."
    )


@router.get("/parsers")
async def list_parsers():
    """List available parsers.
    
    Returns:
        List of available parser names
    """
    parsers = parser_service.get_available_parsers()
    return {"parsers": parsers}
