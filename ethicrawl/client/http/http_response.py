from dataclasses import dataclass, field

from ethicrawl.client.response import Response
from ethicrawl.core import Headers

from .http_request import HttpRequest


@dataclass
class HttpResponse(Response):
    """
    Standardized HTTP response object that's independent of the underlying HTTP library.
    Contains the response data and reference to the original request.
    """

    request: HttpRequest  # pyright: ignore[reportIncompatibleVariableOverride]
    # OSError: HTTP request failed: Error fetching https://www.bbc.co.uk/robots.txt: request must be an Request instance, got HttpRequest
    # content is already in the parent

    status_code: int = 200
    headers: Headers = field(default_factory=Headers)
    text: str = str()  # Only populated for text content

    def __post_init__(self) -> None:
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

        # Validate content and text consistency
        if self.content is not None and not isinstance(self.content, bytes):
            raise TypeError(
                f"content must be bytes or None, got {type(self.content).__name__}"
            )
        if self.text is not None and not isinstance(self.text, str):
            raise TypeError(
                f"text must be a string or None, got {type(self.text).__name__}"
            )

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the response.
        Truncates binary content for readability.
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
