"""PageIndex API routes — proxy to PageIndex API (health, documents, jobs, toc, query)."""
import logging

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from config import settings
from infrastructure.clients.pageindex_client import (
    PageIndexClient,
    PageIndexClientError,
    PageIndexError,
    PageIndexServerError,
)

logger = logging.getLogger(__name__)
router = APIRouter()
client = PageIndexClient(
    base_url=settings.PAGEINDEX_BASE_URL,
    timeout=settings.PAGEINDEX_TIMEOUT,
)


class QueryBody(BaseModel):
    query: str


@router.get("/pageindex/health")
async def pageindex_health():
    """Proxy GET /health to PageIndex."""
    try:
        return client.health()
    except (PageIndexClientError, PageIndexServerError) as e:
        raise HTTPException(
            status_code=502,
            detail=str(e),
        ) from e
    except PageIndexError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@router.post("/pageindex/documents", status_code=202)
async def pageindex_upload_documents(
    files: list[UploadFile] = File(..., description="PDF files"),
):
    """Proxy POST /documents to PageIndex. Returns 202 with job_id."""
    pdfs = [f for f in files if f.filename and f.filename.lower().endswith(".pdf")]
    if not pdfs:
        raise HTTPException(400, "At least one PDF file is required")
    file_list: list[tuple[str, bytes]] = []
    for f in pdfs:
        content = await f.read()
        file_list.append((f.filename or "unnamed.pdf", content))
    try:
        return client.upload_documents(file_list)
    except PageIndexClientError as e:
        raise HTTPException(400, detail=str(e)) from e
    except (PageIndexServerError, PageIndexError) as e:
        raise HTTPException(502, detail=str(e)) from e


@router.get("/pageindex/jobs/{job_id}")
async def pageindex_get_job(job_id: str):
    """Proxy GET /jobs/{job_id} to PageIndex."""
    try:
        return client.get_job(job_id)
    except PageIndexClientError as e:
        if "not found" in str(e).lower():
            raise HTTPException(404, detail="Job not found") from e
        raise HTTPException(400, detail=str(e)) from e
    except (PageIndexServerError, PageIndexError) as e:
        raise HTTPException(502, detail=str(e)) from e


@router.get("/pageindex/documents")
async def pageindex_list_documents():
    """Proxy GET /documents to PageIndex."""
    try:
        return client.list_documents()
    except (PageIndexClientError, PageIndexServerError, PageIndexError) as e:
        raise HTTPException(502, detail=str(e)) from e


@router.get("/pageindex/documents/{document_id}/toc")
async def pageindex_get_toc(document_id: str):
    """Proxy GET /documents/{document_id}/toc to PageIndex."""
    try:
        return client.get_toc(document_id)
    except PageIndexClientError as e:
        if "not found" in str(e).lower():
            raise HTTPException(404, detail="Document not found") from e
        raise HTTPException(400, detail=str(e)) from e
    except (PageIndexServerError, PageIndexError) as e:
        raise HTTPException(502, detail=str(e)) from e


@router.post("/pageindex/documents/{document_id}/query")
async def pageindex_query(document_id: str, body: QueryBody):
    """Proxy POST /documents/{document_id}/query to PageIndex."""
    try:
        return client.query(document_id, body.query)
    except PageIndexClientError as e:
        if "not found" in str(e).lower():
            raise HTTPException(404, detail="Document not found") from e
        raise HTTPException(400, detail=str(e)) from e
    except (PageIndexServerError, PageIndexError) as e:
        raise HTTPException(502, detail=str(e)) from e


@router.delete("/pageindex/documents/{document_id}")
async def pageindex_delete_document(document_id: str):
    """Proxy DELETE /documents/{document_id} to PageIndex."""
    try:
        return client.delete_document(document_id)
    except PageIndexClientError as e:
        if "not found" in str(e).lower():
            raise HTTPException(404, detail="Document not found") from e
        raise HTTPException(400, detail=str(e)) from e
    except (PageIndexServerError, PageIndexError) as e:
        raise HTTPException(502, detail=str(e)) from e
