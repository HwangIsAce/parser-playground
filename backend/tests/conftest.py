"""Pytest configuration and shared fixtures."""
import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

from core.models.document import Document, DocumentStatus
from core.models.parse_result import ParseResult, Block


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_document():
    """Create a sample document for testing."""
    return Document(
        id="test-doc-123",
        filename="test.pdf",
        file_type="pdf",
        file_path="/tmp/test.pdf",
        page_count=1,
        status=DocumentStatus.COMPLETED,
        created_at=datetime.now(),
    )


@pytest.fixture
def sample_image_document():
    """Create a sample image document for testing."""
    return Document(
        id="test-img-123",
        filename="test.png",
        file_type="png",
        file_path="/tmp/test.png",
        page_count=1,
        status=DocumentStatus.COMPLETED,
    )


@pytest.fixture
def sample_parse_result():
    """Create a sample parse result for testing."""
    coordinates = [
        {"x": 0.0, "y": 0.0},
        {"x": 1.0, "y": 0.0},
        {"x": 1.0, "y": 0.5},
        {"x": 0.0, "y": 0.5}
    ]
    blocks = [
        Block(
            type="text",
            text="Sample text content",
            page=1,
            element_id=0,
            metadata={"parser": "unstructured"},
        ),
        Block(
            type="table",
            text="Table content",
            coordinates=coordinates,
            page=1,
            element_id=1,
        ),
    ]
    return ParseResult(
        document_id="test-doc-123",
        blocks=blocks,
        full_content={"html": "<div>...</div>", "markdown": "...", "text": "..."},
        usage={"pages": 1},
        metadata={"parser": "unstructured", "file_type": "pdf"},
    )
