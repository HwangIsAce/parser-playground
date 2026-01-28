"""Parse API routes."""
from fastapi import APIRouter, HTTPException

from api.schemas.parse_result import ParseRequest, ParseResponse
from application.services.parser_service import ParserService
from api.routes.documents import document_service

router = APIRouter()
parser_service = ParserService()


@router.post("/documents/{document_id}/pages/{page_number}/parse", response_model=ParseResponse)
async def parse_document(
    document_id: str,
    page_number: int,
    request: ParseRequest = ParseRequest()
):
    """Parse a specific page of the document.
    
    Args:
        document_id: Document ID
        page_number: Page number (0-indexed)
        request: Parse request with mode ('basic' or 'enhance')
        
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
    
    # Validate mode
    if request.mode not in ["basic", "enhance"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode: {request.mode}. Use 'basic' or 'enhance'"
        )
    
    # Parse document
    try:
        parse_result = parser_service.parse_document(
            document,
            mode=request.mode
        )
        return ParseResponse.from_domain(parse_result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # GPU not available for Chandra
        if "GPU" in str(e) or "CUDA" in str(e):
            raise HTTPException(
                status_code=503,
                detail="Chandra parser requires GPU. GPU is not available."
            )
        raise HTTPException(status_code=500, detail=str(e))
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Parser dependencies not installed: {str(e)}"
        )
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
