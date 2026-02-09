"""HTTP client for Peter-parser API (POST /parse, GET /status, GET /result)."""
import logging
from typing import Dict, Any, Optional

import httpx

logger = logging.getLogger(__name__)

VALID_DOCUMENT_TYPES = ("heading", "plain", "slide", "lifelog", "excel")

# document_type -> allowed extensions
DOCUMENT_TYPE_EXTENSIONS = {
    "heading": [".pdf"],
    "plain": [".pdf"],
    "slide": [".pdf"],
    "lifelog": [".txt"],
    "excel": [".xlsx"],
}


class PeterParserError(Exception):
    """Base exception for Peter-parser API errors."""
    pass


class PeterParserClientError(PeterParserError):
    """Client error (4xx) from Peter-parser API."""
    pass


class PeterParserServerError(PeterParserError):
    """Server error (5xx) from Peter-parser API."""
    pass


class PeterParserClient:
    """HTTP client for Peter-parser API."""

    def __init__(self, base_url: str, timeout: int = 360):
        """Initialize Peter-parser client.

        Args:
            base_url: Base URL of Peter-parser API (e.g. http://localhost:8001)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        logger.info("PeterParserClient initialized: base_url=%s timeout=%ss", self.base_url, self.timeout)

    def parse(self, file_content: bytes, filename: str, document_type: str = "plain") -> Dict[str, Any]:
        """Call Peter-parser POST /parse.

        Args:
            file_content: File content as bytes
            filename: Original filename (used for extension validation)
            document_type: heading | plain | slide | lifelog | excel

        Returns:
            {"job_id": str, "status": "pending"}

        Raises:
            PeterParserClientError: 4xx (invalid document_type, extension mismatch)
            PeterParserServerError: 5xx
            PeterParserError: Other errors
        """
        doc_type = (document_type or "plain").strip().lower()
        self._validate_document_type_and_extension(doc_type, filename)

        url = f"{self.base_url}/parse"
        files = {"file": (filename, file_content)}
        data = {"document_type": doc_type}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, files=files, data=data)
        except httpx.ConnectError as e:
            raise PeterParserError(
                f"Cannot connect to Peter-parser at {self.base_url}. "
                "Ensure Peter-parser server is running (e.g. port 8001)."
            ) from e
        except httpx.TimeoutException as e:
            raise PeterParserError(f"Peter-parser request timeout: {e}") from e
        except httpx.RequestError as e:
            raise PeterParserError(f"Peter-parser request failed: {e}") from e

        return self._handle_response(response, url)

    def get_status(self, job_id: str) -> Dict[str, Any]:
        """Call Peter-parser GET /status/{job_id}.

        Returns:
            {"job_id": str, "status": str, "error": str|None, "created_at": str}
        """
        url = f"{self.base_url}/status/{job_id}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url)
        except httpx.ConnectError as e:
            raise PeterParserError(
                f"Cannot connect to Peter-parser at {self.base_url}. "
                "Ensure Peter-parser server is running."
            ) from e
        except (httpx.TimeoutException, httpx.RequestError) as e:
            raise PeterParserError(f"Peter-parser request failed: {e}") from e
        return self._handle_response(response, url, not_found_ok=True)

    def get_result(self, job_id: str) -> Dict[str, Any]:
        """Call Peter-parser GET /result/{job_id}.

        Returns:
            {"chunks": [...]}
        """
        url = f"{self.base_url}/result/{job_id}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url)
        except httpx.ConnectError as e:
            raise PeterParserError(
                f"Cannot connect to Peter-parser at {self.base_url}. "
                "Ensure Peter-parser server is running."
            ) from e
        except (httpx.TimeoutException, httpx.RequestError) as e:
            raise PeterParserError(f"Peter-parser request failed: {e}") from e
        return self._handle_response(response, url, not_found_ok=True)

    def _validate_document_type_and_extension(self, document_type: str, filename: str) -> None:
        """Validate document_type and file extension match."""
        if document_type not in VALID_DOCUMENT_TYPES:
            raise PeterParserClientError(
                f"document_type must be one of {VALID_DOCUMENT_TYPES}"
            )
        fn_lower = filename.lower()
        allowed = DOCUMENT_TYPE_EXTENSIONS.get(document_type, [])
        if not any(fn_lower.endswith(ext) for ext in allowed):
            raise PeterParserClientError(
                f"For {document_type}, file must have extension {allowed}"
            )

    def _handle_response(
        self, response: httpx.Response, url: str, not_found_ok: bool = False
    ) -> Dict[str, Any]:
        """Handle HTTP response and return JSON or raise."""
        if response.status_code == 404 and not_found_ok:
            raise PeterParserClientError("Job not found")
        if response.status_code >= 500:
            raise PeterParserServerError(
                f"Peter-parser server error: {response.status_code} {response.text}"
            )
        if response.status_code >= 400:
            raise PeterParserClientError(
                f"Peter-parser client error: {response.status_code} {response.text}"
            )
        response.raise_for_status()
        return response.json()
