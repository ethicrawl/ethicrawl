from unittest.mock import MagicMock, patch

from ethicrawl.config import Config
from ethicrawl.context import Context
from ethicrawl.core import Resource
from ethicrawl.client.http import HttpRequest
from ethicrawl.client.http.requests_transport import RequestsTransport


class TestRequestsTransport:
    def get_transport(self) -> RequestsTransport:
        return RequestsTransport(Context(Resource("https://www.google.com")))

    def test_user_agent(self):
        rt = self.get_transport()
        rt.user_agent = "foo"
        assert rt.user_agent == "foo"

    def test_get_request(self):
        # Create a mock response
        mock_response = MagicMock()
        mock_response.url = "https://example.com/redirected"
        mock_response.status_code = 200
        mock_response.text = "Hello, World!"
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.content = b"Hello, World!"

        # Create context and request
        context = Context(Resource("https://example.com"))
        request = HttpRequest("https://example.com", headers={"foo": "bar"})

        Config().http.proxies.http = "http://localhost:3128"
        Config().http.proxies.https = "http://localhost:3128"

        # Mock the session.get method
        with patch("requests.Session.get", return_value=mock_response):
            # Create transport with our mock
            transport = RequestsTransport(context)

            # Execute the method under test
            response = transport.get(request)

            # Assertions
            assert response.status_code == 200
            assert str(response.url) == "https://example.com/redirected"
            assert response.text == "Hello, World!"
            assert "Content-Type".lower() in response.headers

        Config().reset()

    def test_server_error_response(self):
        """Test transport handling of 500-level server error responses."""
        # Create a mock response with a 500-level error
        mock_response = MagicMock()
        mock_response.url = "https://example.com/api"
        mock_response.status_code = 503  # Service Unavailable
        mock_response.text = "Service Unavailable"
        mock_response.headers = {"Content-Type": "text/plain", "Retry-After": "120"}
        mock_response.content = b"Service Unavailable"

        # Create context and request
        context = Context(Resource("https://example.com"))
        request = HttpRequest(
            "https://example.com/api", headers={"User-Agent": "Ethicrawl-Test"}
        )

        # Mock the session.get method to return our error response
        with patch("requests.Session.get", return_value=mock_response):
            # Create transport
            transport = RequestsTransport(context)

            # Execute the request
            response = transport.get(request)

            # Verify the response correctly represents the server error
            assert response.status_code == 503
            assert str(response.url) == "https://example.com/api"
            assert response.text == "Service Unavailable"
            assert "content-type" in response.headers
            assert "retry-after" in response.headers
            assert response.headers["retry-after"] == "120"
            assert response.content == b"Service Unavailable"
