"""Chunking API routes — proxy to Peter-parser (POST /parse, GET /status, GET /result)."""
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from application.services.document_service import DocumentService
from config import settings
from infrastructure.clients.peter_parser_client import (
    PeterParserClient,
    PeterParserClientError,
    PeterParserError,
    PeterParserServerError,
)

router = APIRouter()
document_service = DocumentService()
peter_parser_client = PeterParserClient(
    base_url=settings.PETER_PARSER_BASE_URL,
    timeout=settings.PETER_PARSER_TIMEOUT,
)


@router.post("/chunking/parse", status_code=202)
async def chunking_parse(
    file: UploadFile = File(...),
    document_type: str = Form("plain", description="heading | plain | slide | lifelog | excel"),
):
    """Upload document for chunking. Saves to Playground for viewer, proxies to Peter-parser.

    Returns:
        { job_id, status: "pending", document_id }
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="File required")

    file_content = await file.read()
    doc_type = (document_type or "plain").strip().lower()

    try:
        # 1. Save to Playground (for document viewer / page images)
        document = document_service.create_from_bytes(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type,
        )

        # 2. Send to Peter-parser
        result = peter_parser_client.parse(
            file_content=file_content,
            filename=file.filename,
            document_type=doc_type,
        )

        return {
            "job_id": result["job_id"],
            "status": result.get("status", "pending"),
            "document_id": document.id,
        }
    except PeterParserClientError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PeterParserServerError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except PeterParserError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/chunking/status/{job_id}")
async def chunking_status(job_id: str):
    """Get chunking job status from Peter-parser."""
    try:
        result = peter_parser_client.get_status(job_id)
        return result
    except PeterParserClientError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Job not found")
        raise HTTPException(status_code=400, detail=str(e))
    except (PeterParserServerError, PeterParserError) as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/chunking/result/{job_id}")
async def chunking_result(job_id: str):
    """Get chunking result from Peter-parser (chunks)."""
    try:
        result = peter_parser_client.get_result(job_id)
        return result
    except PeterParserClientError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Job not found")
        raise HTTPException(status_code=400, detail=str(e))
    except (PeterParserServerError, PeterParserError) as e:
        raise HTTPException(status_code=502, detail=str(e))
