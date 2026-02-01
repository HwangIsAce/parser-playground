"""Tests for ParserAPIClient."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import httpx

from infrastructure.clients.parser_api_client import (
    ParserAPIClient,
    ParserAPIError,
    ParserAPITimeoutError,
    ParserAPIServerError,
    ParserAPIClientError,
)


class TestParserAPIClient:
    """Test ParserAPIClient."""
    
    def test_init(self):
        """Test initialization."""
        client = ParserAPIClient(
            base_url="http://localhost:8000",
            timeout=60,
            retry_count=2,
            retry_delay=0.5
        )
        
        assert client.base_url == "http://localhost:8000"
        assert client.timeout == 60
        assert client.retry_count == 2
        assert client.retry_delay == 0.5
    
    def test_init_strips_trailing_slash(self):
        """Test that base_url trailing slash is stripped."""
        client = ParserAPIClient(base_url="http://localhost:8000/")
        assert client.base_url == "http://localhost:8000"
    
    @patch('infrastructure.clients.parser_api_client.httpx.Client')
    def test_process_document_success(self, mock_client_class):
        """Test successful document processing."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "doc-123",
            "text": "Extracted text",
            "metadata": {"page_count": 1},
            "structure": {"sections": []}
        }
        mock_response.raise_for_status = Mock()
        
        # Mock client
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = ParserAPIClient(base_url="http://localhost:8000")
        result = client.process_document("/path/to/file.pdf", b"file content")
        
        assert result["id"] == "doc-123"
        assert result["text"] == "Extracted text"
        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert call_args[0][0] == "POST"
        assert "/v1/documents/process" in call_args[0][1]
    
    @patch('infrastructure.clients.parser_api_client.httpx.Client')
    def test_process_ocr_success(self, mock_client_class):
        """Test successful OCR processing."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "ocr-123",
            "text": "OCR text",
            "markdown": "# Title\nOCR text",
            "html": "<h1>Title</h1>",
            "metadata": {"page_count": 1}
        }
        mock_response.raise_for_status = Mock()
        
        # Mock client
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = ParserAPIClient(base_url="http://localhost:8000")
        result = client.process_ocr(
            "/path/to/image.png",
            b"image content",
            prompt_type="ocr_layout",
            output_format="markdown"
        )
        
        assert result["id"] == "ocr-123"
        assert result["text"] == "OCR text"
        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert call_args[0][0] == "POST"
        assert "/v1/ocr" in call_args[0][1]
        assert call_args[1]["data"]["prompt_type"] == "ocr_layout"
        assert call_args[1]["data"]["output_format"] == "markdown"
    
    @patch('infrastructure.clients.parser_api_client.httpx.Client')
    @patch('infrastructure.clients.parser_api_client.time.sleep')
    def test_request_with_retry_on_timeout(self, mock_sleep, mock_client_class):
        """Test retry logic on timeout."""
        # Mock client that raises TimeoutException
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.request.side_effect = httpx.TimeoutException("Timeout")
        mock_client_class.return_value = mock_client
        
        client = ParserAPIClient(
            base_url="http://localhost:8000",
            retry_count=2,
            retry_delay=0.1
        )
        
        with pytest.raises(ParserAPITimeoutError):
            client.process_document("/path/to/file.pdf", b"content")
        
        # Should retry 2 times
        assert mock_client.request.call_count == 2
        assert mock_sleep.call_count == 1  # One retry delay
    
    @patch('infrastructure.clients.parser_api_client.httpx.Client')
    def test_request_raises_client_error_immediately(self, mock_client_class):
        """Test that 4xx errors are raised immediately without retry."""
        # Mock response with 4xx error
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        
        # Mock client
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = ParserAPIClient(base_url="http://localhost:8000", retry_count=3)
        
        with pytest.raises(ParserAPIClientError, match="HTTP 400"):
            client.process_document("/path/to/file.pdf", b"content")
        
        # Should not retry on 4xx errors
        assert mock_client.request.call_count == 1
    
    @patch('infrastructure.clients.parser_api_client.httpx.Client')
    @patch('infrastructure.clients.parser_api_client.time.sleep')
    def test_request_retries_on_server_error(self, mock_sleep, mock_client_class):
        """Test retry logic on 5xx server errors."""
        # Mock response with 5xx error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        # Mock client
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = ParserAPIClient(
            base_url="http://localhost:8000",
            retry_count=2,
            retry_delay=0.1
        )
        
        with pytest.raises(ParserAPIServerError, match="HTTP 500"):
            client.process_document("/path/to/file.pdf", b"content")
        
        # Should retry 2 times
        assert mock_client.request.call_count == 2
        assert mock_sleep.call_count == 1
    
    @patch('infrastructure.clients.parser_api_client.httpx.Client')
    def test_request_raises_generic_error_after_retries(self, mock_client_class):
        """Test that generic errors are raised after all retries."""
        # Mock client that raises generic exception
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.request.side_effect = Exception("Connection error")
        mock_client_class.return_value = mock_client
        
        client = ParserAPIClient(
            base_url="http://localhost:8000",
            retry_count=2,
            retry_delay=0.1
        )
        
        with pytest.raises(ParserAPIError, match="Failed after 2 attempts"):
            client.process_document("/path/to/file.pdf", b"content")
        
        # Should retry 2 times
        assert mock_client.request.call_count == 2
    
    @patch('infrastructure.clients.parser_api_client.httpx.Client')
    def test_process_ocr_with_default_params(self, mock_client_class):
        """Test process_ocr with default parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "ocr-123", "text": "text"}
        mock_response.raise_for_status = Mock()
        
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = ParserAPIClient(base_url="http://localhost:8000")
        client.process_ocr("/path/to/image.png", b"content")
        
        call_args = mock_client.request.call_args
        assert call_args[1]["data"]["prompt_type"] == "ocr_layout"
        assert call_args[1]["data"]["output_format"] == "markdown"
