"""Document API routes."""
from fastapi import APIRouter, UploadFile, File

from api.schemas.document import DocumentResponse, DocumentCreate

router = APIRouter()


@router.post("/documents", response_model=DocumentResponse, status_code=201)
async def upload_document(file: UploadFile = File(...)):
    """Upload a document."""
    raise NotImplementedError


@router.post("/documents/url", response_model=DocumentResponse, status_code=201)
async def upload_document_from_url(request: DocumentCreate):
    """Upload a document from URL."""
    raise NotImplementedError


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """Get document information."""
    raise NotImplementedError


@router.get("/documents/{document_id}/pages/{page_number}")
async def get_page_image(document_id: str, page_number: int):
    """Get document page image."""
    raise NotImplementedError


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(document_id: str):
    """Delete a document."""
    raise NotImplementedError
