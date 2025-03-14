import pytest
from ethicrawl.client.http_response import HttpResponse
from ethicrawl.client.http_request import HttpRequest
from ethicrawl.core.url import Url


class TestHttpResponse:
    def setup_method(self):
        """Set up test fixtures."""
        self.url = Url("https://example.com")
        self.request = HttpRequest(self.url)

    def test_initialization_minimal(self):
        """Test basic initialization with minimal parameters."""
        response = HttpResponse(status_code=200, request=self.request)

        assert response.status_code == 200
        assert response.request == self.request
        assert response.headers == {}
        assert response.content is None
        assert response.text is None

    def test_initialization_complete(self):
        """Test initialization with all parameters."""
        headers = {"Content-Type": "text/html", "Server": "nginx"}
        content = b"<html><body>Test</body></html>"
        text = "<html><body>Test</body></html>"

        response = HttpResponse(
            status_code=200,
            request=self.request,
            headers=headers,
            content=content,
            text=text,
        )

        assert response.status_code == 200
        assert response.request == self.request
        assert response.headers == headers
        assert response.content == content
        assert response.text == text

    def test_boolean_evaluation(self):
        """Test boolean evaluation of response objects."""
        # Response with status code should evaluate to True
        response = HttpResponse(status_code=200, request=self.request)
        assert bool(response) is True

        # Response with None status code should evaluate to False
        response = HttpResponse(status_code=None, request=self.request)
        assert bool(response) is False

    def test_str_representation_text_content(self):
        """Test string representation with text content."""
        headers = {"Content-Type": "text/html"}
        html = "<html><body>This is a test page</body></html>"

        response = HttpResponse(
            status_code=200,
            request=self.request,
            headers=headers,
            content=html.encode("utf-8"),
            text=html,
        )

        str_repr = str(response)

        # Check basic elements
        assert "HTTP 200" in str_repr
        assert "URL: https://example.com" in str_repr
        assert "Content-Type: text/html" in str_repr
        assert "This is a test page" in str_repr

    def test_str_representation_binary_content(self):
        """Test string representation with binary content."""
        headers = {"Content-Type": "image/jpeg"}
        content = b"\x89PNG\r\n\x1a\n" + b"0" * 100  # Mock binary data

        response = HttpResponse(
            status_code=200, request=self.request, headers=headers, content=content
        )

        str_repr = str(response)

        # Check that binary content is summarized by size, not shown directly
        assert "HTTP 200" in str_repr
        assert "Content-Type: image/jpeg" in str_repr
        content_size = len(content)
        assert f"{content_size} bytes" in str_repr
        assert "Text:" not in str_repr  # No text section for binary

    def test_str_representation_large_text(self):
        """Test string representation with large text that gets truncated."""
        headers = {"Content-Type": "text/plain"}
        # Create text longer than truncation limit
        long_text = "A" * 500

        response = HttpResponse(
            status_code=200,
            request=self.request,
            headers=headers,
            content=long_text.encode("utf-8"),
            text=long_text,
        )

        str_repr = str(response)

        # Check truncation
        assert "..." in str_repr
        assert (
            len(str_repr) < len(long_text) + 200
        )  # Rough check that truncation happened

    def test_str_representation_json_content(self):
        """Test JSON content is treated as text."""
        headers = {"Content-Type": "application/json"}
        json_text = '{"name": "Test", "value": 123}'

        response = HttpResponse(
            status_code=200,
            request=self.request,
            headers=headers,
            content=json_text.encode("utf-8"),
            text=json_text,
        )

        str_repr = str(response)

        # Check JSON is shown in text section
        assert "Text: '" in str_repr
        assert '"name": "Test"' in str_repr

    def test_str_representation_no_content(self):
        """Test string representation with no content."""
        response = HttpResponse(status_code=204, request=self.request)  # No Content

        str_repr = str(response)

        assert "HTTP 204" in str_repr
        assert "Content: None" in str_repr
