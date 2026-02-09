"""Tests for Chunking API (Peter-parser proxy)."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime

from api.app import create_app
from core.models.document import Document, DocumentStatus


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def sample_document():
    """Create sample document for chunking flow."""
    return Document(
        id="chunk-doc-456",
        filename="sample.xlsx",
        file_type="xlsx",
        file_path="/tmp/sample.xlsx",
        page_count=1,
        status=DocumentStatus.COMPLETED,
        created_at=datetime.now(),
        metadata={},
    )


@pytest.fixture
def sample_excel_bytes():
    """Minimal Excel file bytes (fake)."""
    return b"PK\x03\x04"  # xlsx magic bytes


class TestChunkingParse:
    """Test POST /chunking/parse."""

    @patch("api.routes.chunking.peter_parser_client")
    @patch("api.routes.chunking.document_service")
    def test_parse_returns_job_id_and_document_id(
        self, mock_doc_service, mock_parser_client, client, sample_document, sample_excel_bytes
    ):
        """POST /chunking/parse returns job_id and document_id."""
        mock_doc_service.create_from_bytes.return_value = sample_document
        mock_parser_client.parse.return_value = {
            "job_id": "job-abc-123",
            "status": "pending",
        }

        response = client.post(
            "/api/v1/chunking/parse",
            files={"file": ("sample.xlsx", sample_excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"document_type": "excel"},
        )

        assert response.status_code == 202
        data = response.json()
        assert data["job_id"] == "job-abc-123"
        assert data["status"] == "pending"
        assert data["document_id"] == "chunk-doc-456"

    @patch("api.routes.chunking.peter_parser_client")
    @patch("api.routes.chunking.document_service")
    def test_parse_rejects_invalid_document_type(
        self, mock_doc_service, mock_parser_client, client, sample_excel_bytes
    ):
        """POST with invalid document_type returns 400."""
        from infrastructure.clients.peter_parser_client import PeterParserClientError
        mock_doc_service.create_from_bytes.return_value = MagicMock(id="doc-1")
        mock_parser_client.parse.side_effect = PeterParserClientError(
            "document_type must be one of ('heading', 'plain', 'slide', 'lifelog', 'excel')"
        )

        response = client.post(
            "/api/v1/chunking/parse",
            files={"file": ("sample.xlsx", sample_excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"document_type": "invalid"},
        )

        assert response.status_code == 400

    @patch("api.routes.chunking.peter_parser_client")
    @patch("api.routes.chunking.document_service")
    def test_parse_extension_mismatch_returns_400(
        self, mock_doc_service, mock_parser_client, client, sample_excel_bytes
    ):
        """POST with lifelog + .xlsx returns 400."""
        from infrastructure.clients.peter_parser_client import PeterParserClientError
        mock_doc_service.create_from_bytes.return_value = MagicMock(id="doc-1")
        mock_parser_client.parse.side_effect = PeterParserClientError(
            "For lifelog, file must have extension ['.txt']"
        )

        response = client.post(
            "/api/v1/chunking/parse",
            files={"file": ("sample.xlsx", sample_excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"document_type": "lifelog"},
        )

        assert response.status_code == 400
        assert "lifelog" in response.json()["detail"].lower() or "txt" in response.json()["detail"].lower()


class TestChunkingStatus:
    """Test GET /chunking/status/{job_id}."""

    @patch("api.routes.chunking.peter_parser_client")
    def test_status_returns_pending(
        self, mock_parser_client, client
    ):
        """GET status returns job status."""
        mock_parser_client.get_status.return_value = {
            "job_id": "job-123",
            "status": "pending",
            "error": None,
            "created_at": "2025-02-09T12:00:00.000000+00:00",
        }

        response = client.get("/api/v1/chunking/status/job-123")

        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "job-123"
        assert data["status"] == "pending"

    @patch("api.routes.chunking.peter_parser_client")
    def test_status_returns_404_for_unknown_job(
        self, mock_parser_client, client
    ):
        """GET status for unknown job returns 404."""
        from infrastructure.clients.peter_parser_client import PeterParserClientError
        mock_parser_client.get_status.side_effect = PeterParserClientError("Job not found")

        response = client.get("/api/v1/chunking/status/nonexistent-job")

        assert response.status_code == 404


class TestChunkingResult:
    """Test GET /chunking/result/{job_id}."""

    @patch("api.routes.chunking.peter_parser_client")
    def test_result_returns_chunks(
        self, mock_parser_client, client
    ):
        """GET result returns chunks when completed."""
        mock_parser_client.get_result.return_value = {
            "chunks": [
                {
                    "uuid": "chunk-1",
                    "doc_title": "sample",
                    "chunk": "Hello world",
                    "chunk_order": 0,
                    "metadata": {"doc_page": [1]},
                }
            ]
        }

        response = client.get("/api/v1/chunking/result/job-123")

        assert response.status_code == 200
        data = response.json()
        assert "chunks" in data
        assert len(data["chunks"]) == 1
        assert data["chunks"][0]["chunk"] == "Hello world"

    @patch("api.routes.chunking.peter_parser_client")
    def test_result_returns_404_for_unknown_job(
        self, mock_parser_client, client
    ):
        """GET result for unknown job returns 404."""
        from infrastructure.clients.peter_parser_client import PeterParserClientError
        mock_parser_client.get_result.side_effect = PeterParserClientError("Job not found")

        response = client.get("/api/v1/chunking/result/nonexistent-job")

        assert response.status_code == 404


class TestChunkingE2EFlow:
    """E2E flow: POST parse -> poll status -> GET result (mocked, no real network)."""

    @patch("api.routes.chunking.peter_parser_client")
    @patch("api.routes.chunking.document_service")
    def test_e2e_chunking_flow(
        self, mock_doc_service, mock_parser_client, client, sample_document, sample_excel_bytes
    ):
        """Full chunking flow: parse -> status pending -> status completed -> result with chunks."""
        mock_doc_service.create_from_bytes.return_value = sample_document
        mock_parser_client.parse.return_value = {
            "job_id": "job-e2e-001",
            "status": "pending",
        }
        mock_parser_client.get_status.side_effect = [
            {"job_id": "job-e2e-001", "status": "pending", "error": None, "created_at": "2025-02-09T12:00:00Z"},
            {"job_id": "job-e2e-001", "status": "completed", "error": None, "created_at": "2025-02-09T12:00:00Z"},
        ]
        mock_parser_client.get_result.return_value = {
            "chunks": [
                {"uuid": "c1", "doc_title": "sample", "chunk": "E2E chunk text", "chunk_order": 0, "metadata": {}},
            ]
        }

        # 1. POST parse
        r1 = client.post(
            "/api/v1/chunking/parse",
            files={"file": ("sample.xlsx", sample_excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"document_type": "excel"},
        )
        assert r1.status_code == 202
        job_id = r1.json()["job_id"]
        assert job_id == "job-e2e-001"

        # 2. GET status (pending then completed)
        r2 = client.get(f"/api/v1/chunking/status/{job_id}")
        assert r2.status_code == 200
        assert r2.json()["status"] in ("pending", "completed")

        r3 = client.get(f"/api/v1/chunking/status/{job_id}")
        assert r3.status_code == 200
        assert r3.json()["status"] == "completed"

        # 3. GET result
        r4 = client.get(f"/api/v1/chunking/result/{job_id}")
        assert r4.status_code == 200
        data = r4.json()
        assert "chunks" in data
        assert len(data["chunks"]) == 1
        assert data["chunks"][0]["chunk"] == "E2E chunk text"
