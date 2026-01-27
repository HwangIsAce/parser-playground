"""API test fixtures."""
import pytest
from fastapi.testclient import TestClient

from api.app import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def sample_file_content():
    """Sample file content for testing."""
    return b"fake pdf content"


@pytest.fixture
def sample_document_id():
    """Sample document ID for testing."""
    return "test-doc-123"
