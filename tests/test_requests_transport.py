import pytest
from unittest.mock import patch, MagicMock
import requests

from ethicrawl.client.requests_transport import RequestsTransport
from ethicrawl.client.http_request import HttpRequest
from ethicrawl.client.http_response import HttpResponse
from ethicrawl.core.context import Context
from ethicrawl.core.resource import Resource
from ethicrawl.core.url import Url


class TestRequestsTransport:
    def setup_method(self):
        """Set up test fixtures."""
        # Create a mock client and context
        self.mock_client = MagicMock()
        self.resource = Resource("https://example.com")

        with patch("ethicrawl.core.context.isinstance", return_value=True):
            self.context = Context(self.resource, self.mock_client)

        # Create the transport
        self.transport = RequestsTransport(self.context)

    def test_get_successful_request(self):
        """Test successful GET request."""
        # Create a request
        request = HttpRequest(Url("https://example.com/test"))
        request.timeout = 30
        request.headers = {"Custom-Header": "Value"}

        # Mock the requests.Session.get method
        with patch.object(self.transport.session, "get") as mock_get:
            # Create mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html>Test content</html>"
            mock_response.content = b"<html>Test content</html>"
            mock_response.headers = {"Content-Type": "text/html", "Server": "nginx"}
            mock_get.return_value = mock_response

            # Call the method
            response = self.transport.get(request)

            # Verify the request was made correctly
            mock_get.assert_called_once()
            call_args = mock_get.call_args[1]
            assert call_args["timeout"] == 30
            assert "Custom-Header" in call_args["headers"]
            assert call_args["headers"]["Custom-Header"] == "Value"
            assert "User-Agent" in call_args["headers"]

            # Verify the response was converted properly
            assert isinstance(response, HttpResponse)
            assert response.status_code == 200
            assert response.text == "<html>Test content</html>"
            assert response.content == b"<html>Test content</html>"
            assert response.headers["Content-Type"] == "text/html"
            assert response.headers["Server"] == "nginx"
            assert response.request == request

    def test_get_request_no_custom_headers(self):
        """Test GET request with no custom headers."""
        # Create a request with no custom headers
        request = HttpRequest(Url("https://example.com/test"))
        request.headers = None  # Explicitly set to None

        # Mock the requests.Session.get method
        with patch.object(self.transport.session, "get") as mock_get:
            # Create mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "Response"
            mock_response.content = b"Response"
            mock_response.headers = {}
            mock_get.return_value = mock_response

            # Call the method
            self.transport.get(request)

            # Verify session headers are present but no custom headers
            call_args = mock_get.call_args[1]
            headers = call_args["headers"]
            assert "User-Agent" in headers
            # Don't assert len(headers) since session might have default headers

    def test_get_request_empty_headers_dict(self):
        """Test GET request with empty headers dictionary."""
        # Create a request with empty headers dictionary
        request = HttpRequest(Url("https://example.com/test"))
        request.headers = {}  # Empty dict, not None

        # Mock the requests.Session.get method
        with patch.object(self.transport.session, "get") as mock_get:
            # Create mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "Response"
            mock_response.content = b"Response"
            mock_response.headers = {}
            mock_get.return_value = mock_response

            # Call the method
            self.transport.get(request)

            # Verify session headers are present but no custom headers were added
            call_args = mock_get.call_args[1]
            headers = call_args["headers"]
            assert "User-Agent" in headers
            # Don't assert len(headers) since session might have default headers

    def test_get_request_error_handling(self):
        """Test error handling during GET request."""
        # Create a request
        request = HttpRequest(Url("https://example.com/error"))

        # Test different types of exceptions
        exceptions_to_test = [
            requests.ConnectionError("Connection refused"),
            requests.Timeout("Request timed out"),
            requests.RequestException("General error"),
            Exception("Unexpected error"),
        ]

        for exception in exceptions_to_test:
            # Mock the session.get method to raise the exception
            with patch.object(self.transport.session, "get") as mock_get:
                mock_get.side_effect = exception

                # Verify the exception is wrapped in IOError
                with pytest.raises(IOError) as excinfo:
                    self.transport.get(request)

                # Check error message contains URL and original exception
                error_msg = str(excinfo.value)
                assert "Error fetching https://example.com/error" in error_msg
                assert str(exception) in error_msg
