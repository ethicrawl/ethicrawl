# FIXME: remove comment, imports sorted

from dataclasses import dataclass, field
from typing import Dict

from ethicrawl.client.response import Response
from ethicrawl.core import Headers

from .http_request import HttpRequest


@dataclass
class HttpResponse(Response):
    """
    Standardized HTTP response object that's independent of the underlying HTTP library.
    Contains the response data and reference to the original request.
    """

    status_code: int
    request: HttpRequest
    headers: Headers = field(default_factory=Headers)
    content: bytes = None  # Raw binary content
    text: str = None  # Only populated for text content

    def __post_init__(self):
        # Call parent's post_init if it exists
        super().__post_init__()

        # Validate status code
        if not isinstance(self.status_code, int):
            raise TypeError("status_code must be an integer")
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
            raise TypeError("content must be bytes or None")
        if self.text is not None and not isinstance(self.text, str):
            raise TypeError("text must be a string or None")

    def __str__(self):
        """
        Return a human-readable string representation of the response.
        Truncates binary content for readability.
        """
        status_line = f"HTTP {self.status_code}"
        url_line = f"URL: {self.url}"
        request_url_line = f"Request URL: {self.request.url}"  # Only if they differ
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
            if self.headers.get("Content-Type", "").startswith("text/"):
                # For text content, show a preview
                preview = self.text[:200] if self.text else ""
                if self.text and len(self.text) > 200:
                    preview += "..."
                content_summary = f"'{preview}'"
            else:
                # For binary content, just show the size
                content_summary = f"{len(self.content)} bytes"

        # Check if it's a text content type before showing text preview
        content_type = self.headers.get("Content-Type", "").lower()
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
