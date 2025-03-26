from dataclasses import dataclass, field

from ethicrawl.client.response import Response
from ethicrawl.core import Headers

from .http_request import HttpRequest


@dataclass
class HttpResponse(Response):
    """HTTP-specific response implementation with status codes and text content.

    This class extends the base Response with HTTP-specific attributes and behaviors,
    including status code, headers, and separate text content representation. It
    provides robust validation and a comprehensive string representation for
    debugging and logging.

    The HttpResponse maintains the connection between the original request and
    the response while enforcing type safety and data consistency.

    Attributes:
        request (HttpRequest): The request that generated this response
        status_code (int): HTTP status code (200, 404, etc.)
        headers (Headers): HTTP response headers
        content (bytes): Binary content of the response (inherited from Response)
        text (str): Text content decoded from binary content (for text responses)
        url (Url): The response URL, which may differ from request URL after redirects

    Example:
        >>> from ethicrawl.client.http import HttpRequest, HttpResponse
        >>> from ethicrawl.core import Resource, Headers
        >>> req = HttpRequest(Resource("https://example.com"))
        >>> resp = HttpResponse(
        ...     request=req,
        ...     status_code=200,
        ...     content=b"<html>Example</html>",
        ...     text="<html>Example</html>",
        ...     headers=Headers({"Content-Type": "text/html"})
        ... )
        >>> resp.status_code
        200
        >>> "html" in resp.text
        True
    """

    request: HttpRequest  # type: ignore # Intentional override with more specific type
    status_code: int = 200
    headers: Headers = field(default_factory=Headers)
    text: str = str()  # Only populated for text content

    def __post_init__(self) -> None:
        """Validate the response attributes after initialization.

        Performs type checking and value validation for:
        - Status code (must be int between 100-599)
        - Request (must be HttpRequest instance)
        - Content (must be bytes or None)
        - Text (must be str or None)

        Also calls the parent class __post_init__ for further validation.

        Raises:
            TypeError: If any attribute has an invalid type
            ValueError: If status_code is outside valid HTTP range (100-599)
        """
        # Call parent's post_init if it exists
        if self.request is None:
            raise TypeError("request must be an HttpRequest instance, got NoneType")
        super().__post_init__()

        # Validate status code
        if not isinstance(self.status_code, int):
            raise TypeError(f"Expected int, got {type(self.status_code).__name__}")
        if self.status_code < 100 or self.status_code > 599:
            raise ValueError(
                f"Invalid HTTP status code: {self.status_code}. Must be between 100 and 599."
            )

        # Validate request
        if not isinstance(self.request, HttpRequest):
            raise TypeError(
                f"request must be an HttpRequest instance, got {type(self.request).__name__}"
            )

        # Validate text consistency, content is handled by Response
        if self.text is not None and not isinstance(self.text, str):
            raise TypeError(
                f"text must be a string or None, got {type(self.text).__name__}"
            )

    def __str__(self) -> str:
        """Format a human-readable representation of the response.

        Creates a formatted multi-line string containing:
        - Status code
        - URL (showing both response URL and request URL if they differ)
        - Headers
        - Content summary (preview for text, byte count for binary)
        - Text preview for text content types (up to 300 chars)

        Returns:
            String representation of the response with formatted content preview
        """
        status_line = f"HTTP {self.status_code}"
        url_line = f"URL: {self.url}"
        # Only if they differ
        request_url_line = f"Request URL: {self.request.url}"
        url_display = (
            f"{url_line}\n{request_url_line}"
            if str(self.url) != str(self.request.url)
            else url_line
        )

        # Format the headers nicely
        headers_str = "\n".join(f"{k}: {v}" for k, v in self.headers.items())

        # Handle content display - summarize if binary
        content_summary = "None"
        if self.content:
            content_type: str = self.headers.get("Content-Type", "") or ""
            if content_type.startswith("text/"):
                # For text content, show a preview
                preview = self.text[:200] if self.text else ""
                if self.text and len(self.text) > 200:
                    preview += "..."
                content_summary = f"'{preview}'"
            else:
                # For binary content, just show the size
                content_summary = f"{len(self.content)} bytes"

        # Check if it's a text content type before showing text preview
        content_type = self.headers.get("Content-Type", "") or ""
        is_text = (
            content_type.startswith("text/")
            or "json" in content_type
            or "xml" in content_type
            or "javascript" in content_type
            or "html" in content_type
        )

        # Show text section only for text content types
        text_section = ""
        if self.text and is_text:
            # Limit text preview to 300 characters
            text_preview = self.text[:300]
            if len(self.text) > 300:
                text_preview += "..."

            # Format with proper line breaks
            text_section = f"\n\nText: '{text_preview}'"

        return f"{status_line}\n{url_display}\n\nHeaders:\n{headers_str}\n\nContent: {content_summary}{text_section}"
