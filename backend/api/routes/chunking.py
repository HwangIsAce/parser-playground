"""Chunking API routes — proxy to Peter-parser (POST /parse, GET /status, GET /result)."""
import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from application.services.document_service import DocumentService
from config import settings
from infrastructure.clients.peter_parser_client import (
    PeterParserClient,
    PeterParserClientError,
    PeterParserError,
    PeterParserServerError,
)

logger = logging.getLogger(__name__)
router = APIRouter()
document_service = DocumentService()
peter_parser_client = PeterParserClient(
    base_url=settings.PETER_PARSER_BASE_URL,
    timeout=settings.PETER_PARSER_TIMEOUT,
)


@router.get("/chunking/config")
async def chunking_config():
    """Development: show where chunking requests are sent (no secrets)."""
    return {
        "peter_parser_base_url": settings.PETER_PARSER_BASE_URL,
        "timeout": settings.PETER_PARSER_TIMEOUT,
    }


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
    logger.info(
        "Chunking request: filename=%s document_type=%s size=%d → Peter-parser=%s",
        file.filename,
        doc_type,
        len(file_content),
        settings.PETER_PARSER_BASE_URL,
    )

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
        logger.info("Chunking → Peter-parser OK: job_id=%s", result.get("job_id"))

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
    except Exception as e:
        logger.exception("Chunking parse failed: %s", e)
        err_msg = str(e)
        if "redis" in err_msg.lower() or "connection refused" in err_msg.lower():
            detail = f"Redis 연결 실패. Redis가 실행 중인지 확인하세요. ({err_msg})"
        elif "8001" in err_msg or "peter-parser" in err_msg.lower():
            detail = f"Peter-parser(8001) 연결 실패. 서버가 실행 중인지 확인하세요. ({err_msg})"
        else:
            detail = f"Internal error: {err_msg}"
        raise HTTPException(status_code=500, detail=detail) from e


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
    except Exception as e:
        logger.exception("Chunking status failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


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
    except Exception as e:
        logger.exception("Chunking result failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
