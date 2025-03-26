from time import time
import pytest
from unittest.mock import MagicMock, patch

from ethicrawl.context import Context
from ethicrawl.core import Resource
from ethicrawl.client.http import HttpClient, HttpRequest, HttpResponse


class TestHttpClient:
    pass

    # def get_transport(self) -> RequestsTransport:
    #     return RequestsTransport(Context(Resource("https://www.google.com")))

    def test_client_instantiation(self):
        client = HttpClient()
        context = client._context
        transport = client.transport
        client.user_agent = "foo"
        assert client.user_agent == "foo"
        client = HttpClient(context)
        client = HttpClient(context, transport)
        client = HttpClient(transport=transport)
        client = HttpClient().with_chrome()
        client = None

    def test_rate_limiting(self):
        # Create mocks
        mock_transport = MagicMock()
        mock_response = MagicMock(spec=HttpResponse)

        # Configure mock response with realistic properties
        mock_response.status_code = 200  # Set a numeric status code
        mock_response.content = b"Test content"  # Add some content

        mock_transport.get.return_value = mock_response

        # Create test resource
        resource = Resource("https://example.com")

        # Create client with aggressive rate limiting
        client = HttpClient(
            context=Context(resource),
            rate_limit=10.0,  # 10 requests per second max
            jitter=0.001,  # Tiny jitter for predictable testing
        )
        client.transport = mock_transport
        client.last_request_time = time()  # Set initial request time

        # First request should trigger rate limiting
        start_time = time()
        client.get(resource)
        elapsed = time() - start_time

        # Should have waited at least the minimum interval
        assert elapsed >= 0.1, f"Rate limiting didn't work, elapsed: {elapsed}"

    def test_get_request(self):
        # Create mocks
        mock_transport = MagicMock()
        mock_response = MagicMock(spec=HttpResponse)

        # Configure mock response with realistic properties
        mock_response.status_code = 200  # Set a numeric status code
        mock_response.content = b"Test content"  # Add some content

        mock_transport.get.return_value = mock_response

        # Create test resource
        resource = Resource("https://example.com")

        # Create client with mocked transport
        client = HttpClient(context=Context(resource))
        client.transport = mock_transport

        # Make request
        response = client.get(resource, headers={"Custom": "Header"}, timeout=5)

        # Verify the transport was called correctly
        mock_transport.get.assert_called_once()

        # Get the HttpRequest that was passed to transport.get()
        request_arg = mock_transport.get.call_args[0][0]
        assert isinstance(request_arg, HttpRequest)
        assert str(request_arg.url) == "https://example.com"
        assert "Custom".lower() in request_arg.headers
        assert request_arg.headers["Custom"] == "Header"

        # Verify we got the expected response
        assert response == mock_response

    def test_bad_input(self):
        resource = Resource("https://example.com")
        # Create client with mocked transport
        client = HttpClient(context=Context(resource))
        with pytest.raises(TypeError, match="Expected Resource object, got str"):
            client.get("foo")

    def test_server_error_response(self):
        """Test client behavior with 500-level server error responses."""
        # Create mocks
        mock_transport = MagicMock()
        mock_response = MagicMock(spec=HttpResponse)

        # Configure mock response as a 500 server error
        mock_response.status_code = 503  # Service Unavailable
        mock_response.content = b"Server Error"
        mock_response.text = "Server Error"
        mock_response.headers = {"Content-Type": "text/plain"}

        mock_transport.get.return_value = mock_response

        # Create test resource
        resource = Resource("https://example.com/api/data")

        # Create client with mocked transport
        client = HttpClient(context=Context(resource))
        client.transport = mock_transport

        # Make request - the client should return the error response without raising
        response = client.get(resource)

        # Verify we got the expected 500 response
        assert response == mock_response
        assert response.status_code == 503

        # Verify the transport was called correctly
        mock_transport.get.assert_called_once()

        # Check the request that was passed to transport
        request_arg = mock_transport.get.call_args[0][0]
        assert isinstance(request_arg, HttpRequest)
        assert str(request_arg.url) == "https://example.com/api/data"
