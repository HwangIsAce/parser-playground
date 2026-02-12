"""HTTP client for PageIndex API (documents, jobs, toc, query)."""
import logging
from typing import Any, Dict, List, Tuple

import httpx

logger = logging.getLogger(__name__)


class PageIndexError(Exception):
    """Base exception for PageIndex API errors."""
    pass


class PageIndexClientError(PageIndexError):
    """Client error (4xx) from PageIndex API."""
    pass


class PageIndexServerError(PageIndexError):
    """Server error (5xx) from PageIndex API."""
    pass


class PageIndexClient:
    """HTTP client for PageIndex API."""

    def __init__(self, base_url: str, timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        logger.info(
            "PageIndexClient initialized: base_url=%s timeout=%ss",
            self.base_url,
            self.timeout,
        )

    def _handle_response(self, response: httpx.Response, url: str) -> Dict[str, Any]:
        if response.status_code >= 500:
            raise PageIndexServerError(
                f"PageIndex server error: {response.status_code} {response.text}"
            )
        if response.status_code == 429:
            raise PageIndexClientError("Rate limit exceeded (10/min)")
        if response.status_code >= 400:
            raise PageIndexClientError(
                f"PageIndex client error: {response.status_code} {response.text}"
            )
        response.raise_for_status()
        return response.json() if response.content else {}

    def health(self) -> Dict[str, Any]:
        """GET /health."""
        url = f"{self.base_url}/health"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url)
        return self._handle_response(response, url)

    def upload_documents(
        self, files: List[Tuple[str, bytes]]
    ) -> Dict[str, Any]:
        """POST /documents (multipart). Returns 202 with job_id."""
        if not files:
            raise PageIndexClientError("At least one PDF file is required")
        url = f"{self.base_url}/documents"
        # PageIndex expects multiple files under "files" (plural)
        file_tuples = [(f"files", (name, content)) for name, content in files]
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, files=file_tuples)
        if response.status_code == 202:
            return response.json()
        return self._handle_response(response, url)

    def get_job(self, job_id: str) -> Dict[str, Any]:
        """GET /jobs/{job_id}."""
        url = f"{self.base_url}/jobs/{job_id}"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url)
        if response.status_code == 404:
            raise PageIndexClientError("Job not found")
        return self._handle_response(response, url)

    def list_documents(self) -> Dict[str, Any]:
        """GET /documents."""
        url = f"{self.base_url}/documents"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url)
        return self._handle_response(response, url)

    def get_toc(self, document_id: str) -> Dict[str, Any]:
        """GET /documents/{document_id}/toc."""
        url = f"{self.base_url}/documents/{document_id}/toc"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url)
        if response.status_code == 404:
            raise PageIndexClientError("Document not found")
        return self._handle_response(response, url)

    def query(self, document_id: str, query: str) -> Dict[str, Any]:
        """POST /documents/{document_id}/query with {"query": "..."}."""
        url = f"{self.base_url}/documents/{document_id}/query"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, json={"query": query})
        if response.status_code == 404:
            raise PageIndexClientError("Document not found")
        return self._handle_response(response, url)

    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """DELETE /documents/{document_id}."""
        url = f"{self.base_url}/documents/{document_id}"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.delete(url)
        if response.status_code == 404:
            raise PageIndexClientError("Document not found")
        return self._handle_response(response, url)
