"""HTTP client for remote parser API."""
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional

import httpx

logger = logging.getLogger(__name__)


class ParserAPIError(Exception):
    """Base exception for parser API errors."""
    pass


class ParserAPITimeoutError(ParserAPIError):
    """Timeout error when calling parser API."""
    pass


class ParserAPIServerError(ParserAPIError):
    """Server error (5xx) when calling parser API."""
    pass


class ParserAPIClientError(ParserAPIError):
    """Client error (4xx) when calling parser API."""
    pass


class ParserAPIClient:
    """HTTP client for remote parser API (synchronous).
    
    This client handles communication with the remote parser API server.
    It uses httpx.SyncClient for synchronous HTTP requests, making it
    compatible with the RQ worker environment.
    """
    
    def __init__(
        self,
        base_url: str,
        timeout: int = 360,
        retry_count: int = 3,
        retry_delay: float = 1.0
    ):
        """Initialize parser API client.
        
        Args:
            base_url: Base URL of the parser API server
            timeout: Request timeout in seconds (default: 360)
            retry_count: Number of retry attempts (default: 3)
            retry_delay: Delay between retries in seconds (default: 1.0)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        logger.info("ParserAPIClient initialized: base_url=%s timeout=%ss", self.base_url, self.timeout)
    
    def process_document(
        self,
        file_path: str,
        file_content: bytes
    ) -> Dict[str, Any]:
        """Call Docling /v1/documents/process endpoint.
        
        Args:
            file_path: Path to file (for filename extraction)
            file_content: File content as bytes
            
        Returns:
            API response as dict with keys: id, text, metadata, structure
            
        Raises:
            ParserAPIError: If API call fails
        """
        url = f"{self.base_url}/v1/documents/process"
        
        # Extract filename from path
        filename = Path(file_path).name
        
        files = {
            "file": (filename, file_content)
        }
        
        logger.info(f"Calling Docling API: {url} with file: {filename}")
        return self._request_with_retry("POST", url, files=files)
    
    def process_ocr(
        self,
        file_path: str,
        file_content: bytes,
        prompt_type: str = "ocr_layout",
        output_format: str = "markdown"
    ) -> Dict[str, Any]:
        """Call Chandra /v1/ocr endpoint.
        
        Args:
            file_path: Path to file (for filename extraction)
            file_content: File content as bytes
            prompt_type: 'ocr_layout' or 'ocr_raw' (default: 'ocr_layout')
            output_format: 'markdown', 'html', or 'json' (default: 'markdown')
            
        Returns:
            API response as dict with keys: id, text, markdown, html, json, metadata
            
        Raises:
            ParserAPIError: If API call fails
        """
        url = f"{self.base_url}/v1/ocr"
        
        filename = Path(file_path).name
        
        files = {
            "image": (filename, file_content)
        }
        data = {
            "prompt_type": prompt_type,
            "output_format": output_format
        }
        
        logger.info(f"Calling Chandra API: {url} with file: {filename}, prompt_type: {prompt_type}")
        return self._request_with_retry("POST", url, files=files, data=data)
    
    def _request_with_retry(
        self,
        method: str,
        url: str,
        files: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (e.g., 'POST')
            url: Request URL
            files: Files to upload (multipart/form-data)
            data: Form data
            
        Returns:
            JSON response as dict
            
        Raises:
            ParserAPITimeoutError: If request times out
            ParserAPIServerError: If server returns 5xx error
            ParserAPIClientError: If server returns 4xx error
            ParserAPIError: For other errors
        """
        last_error = None
        
        for attempt in range(1, self.retry_count + 1):
            try:
                logger.debug(f"Attempt {attempt}/{self.retry_count}: {method} {url}")
                
                # Use httpx SyncClient for synchronous requests
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.request(
                        method,
                        url,
                        files=files,
                        data=data
                    )
                    
                    logger.debug(f"Response status: {response.status_code}")
                    
                    # Check for HTTP errors
                    if response.status_code >= 500:
                        last_error = f"HTTP {response.status_code}: {response.text}"
                        logger.warning(f"Server error: {last_error}")
                        if attempt == self.retry_count:
                            raise ParserAPIServerError(last_error)
                    
                    elif response.status_code >= 400:
                        last_error = f"HTTP {response.status_code}: {response.text}"
                        logger.error(f"Client error: {last_error}")
                        raise ParserAPIClientError(last_error)
                    
                    # Success
                    response.raise_for_status()
                    result = response.json()
                    logger.info(f"API call successful: {method} {url}")
                    return result
            
            except httpx.TimeoutException as e:
                last_error = f"Request timeout after {self.timeout}s: {str(e)}"
                logger.warning(f"Attempt {attempt}/{self.retry_count}: {last_error}")
                if attempt == self.retry_count:
                    raise ParserAPITimeoutError(last_error)
            
            except (ParserAPIClientError, ParserAPIServerError):
                # Don't retry on client errors (4xx), re-raise immediately
                raise
            
            except httpx.HTTPStatusError as e:
                last_error = f"HTTP {e.response.status_code}: {e.response.text}"
                logger.error(f"Attempt {attempt}/{self.retry_count}: {last_error}")
                if attempt == self.retry_count:
                    raise ParserAPIError(last_error)
            
            except Exception as e:
                err_str = str(e)
                if "61" in err_str or "Connection refused" in err_str or "Errno 61" in err_str:
                    last_error = (
                        f"Connection refused to {self.base_url}. "
                        "Check that the parser server is running and reachable "
                        "(PARSER_API_BASE_URL in config or .env)."
                    )
                else:
                    last_error = f"Unexpected error: {err_str}"
                logger.error(f"Attempt {attempt}/{self.retry_count}: {last_error}")
                if attempt == self.retry_count:
                    raise ParserAPIError(last_error)
            
            # Wait before retry (exponential backoff)
            if attempt < self.retry_count:
                delay = self.retry_delay * (2 ** (attempt - 1))
                logger.debug(f"Waiting {delay}s before retry...")
                time.sleep(delay)
        
        # Should not reach here, but just in case
        raise ParserAPIError(f"Failed after {self.retry_count} attempts: {last_error}")
