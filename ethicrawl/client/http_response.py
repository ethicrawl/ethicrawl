from dataclasses import dataclass, field
from typing import Dict
from ethicrawl.client.http_request import HttpRequest


@dataclass
class HttpResponse:
    """
    Standardized HTTP response object that's independent of the underlying HTTP library.
    Contains the response data and reference to the original request.
    """

    status_code: int
    request: HttpRequest
    headers: Dict = field(default_factory=dict)
    content: bytes = None  # Raw binary content
    text: str = None  # Only populated for text content

    def __bool__(self):
        """Allow response to be used in boolean context - True if we got any response"""
        return self.status_code is not None

    def __str__(self):
        """
        Return a human-readable string representation of the response.
        Truncates binary content for readability.
        """
        status_line = f"HTTP {self.status_code}"
        url_line = f"URL: {self.request.url}"

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

        return f"{status_line}\n{url_line}\n\nHeaders:\n{headers_str}\n\nContent: {content_summary}{text_section}"
