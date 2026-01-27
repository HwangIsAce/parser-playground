"""Parse API routes."""
from fastapi import APIRouter

from api.schemas.parse_result import ParseRequest, ParseResponse

router = APIRouter()


@router.post("/documents/{document_id}/parse", response_model=ParseResponse)
async def parse_document(document_id: str, request: ParseRequest):
    """Parse a document."""
    raise NotImplementedError


@router.get("/documents/{document_id}/parse/result")
async def get_parse_result(document_id: str, format: str = "blocks"):
    """Get parse result in different formats."""
    raise NotImplementedError


@router.get("/parsers")
async def list_parsers():
    """List available parsers."""
    raise NotImplementedError
