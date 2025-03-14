import pytest
from unittest.mock import MagicMock, patch
from ethicrawl.client.http_client import HttpClient
from ethicrawl.client.http_response import HttpResponse
from ethicrawl.core.resource import Resource
from ethicrawl.core.url import Url


class TestHttpClient:
    def test_client_initialization(self):
        """Test HTTP client creation with default parameters."""
        client = HttpClient()

        # Check default attributes instead of a config object
        assert client.timeout == 10  # Default timeout
        assert client.min_interval > 0  # Rate limiting enabled
        assert client.jitter == 0.5  # Default jitter
        assert client.transport is not None  # Transport should be created
        assert hasattr(client, "user_agent")  # Should have user_agent property

    @patch("ethicrawl.client.requests_transport.RequestsTransport.get")
    def test_client_get_request(self, mock_get):
        """Test HTTP GET request."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.body = "<html><body>Test</body></html>"
        mock_get.return_value = mock_response

        # Create client and make request
        client = HttpClient()
        response = client.get(Resource("https://example.com"))

        # Verify response
        assert response.status_code == 200
        assert response.body == "<html><body>Test</body></html>"
        mock_get.assert_called_once()

    def test_with_different_url_types(self):
        """Test handling different URL input types."""
        with patch(
            "ethicrawl.client.requests_transport.RequestsTransport.get"
        ) as mock_get:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.body = "<html></html>"
            mock_get.return_value = mock_response

            client = HttpClient()

            # Test with string URL - should be converted to Resource
            with pytest.raises(TypeError):
                client.get("https://example.com/page")

            # Test with Resource
            resource = Resource("https://example.com/page")
            response = client.get(resource)
            assert response.status_code == 200

            # Reset mock to check it was called
            mock_get.assert_called()

    def test_rate_limiting(self):
        """Test that rate limiting delays between requests."""
        with patch(
            "ethicrawl.client.requests_transport.RequestsTransport.get"
        ) as mock_get, patch("time.sleep") as mock_sleep:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            # Create client with strict rate limiting (1 req/sec)
            client = HttpClient(rate_limit=1.0, jitter=0)

            # First request shouldn't sleep
            client.get(Resource("https://example.com"))
            mock_sleep.assert_not_called()

            # Second request should trigger rate limiting
            client.get(Resource("https://example.com"))
            mock_sleep.assert_called()
