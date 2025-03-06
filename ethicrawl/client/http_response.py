from typing import Dict, Any, Optional


class HttpResponse:
    """
    Standardized HTTP response object that's independent of the underlying HTTP library.
    """

    def __init__(
        self, status_code: int, text: str, headers: Dict = None, content: bytes = None
    ):
        self.status_code = status_code
        self._text = text
        self.headers = headers or {}
        self._content = content

    @property
    def content(self) -> bytes:
        """Raw binary response content"""
        return self._content

    @property
    def text(self) -> str:
        """
        Response content decoded to string.
        Uses encoding from Content-Type header or falls back to UTF-8.
        """
        if self._text is None:
            # Try to extract encoding from headers or default to utf-8
            content_type = self.headers.get("Content-Type", "")
            encoding = "utf-8"  # Default encoding

            # Extract charset from Content-Type if available
            if "charset=" in content_type.lower():
                encoding = (
                    content_type.lower().split("charset=")[1].split(";")[0].strip()
                )

            # Decode content with appropriate encoding
            self._text = self._content.decode(encoding, errors="replace")

        return self._text

    def is_success(self) -> bool:
        """Check if the response indicates success (2xx status code)"""
        return 200 <= self.status_code < 300

    def __bool__(self):
        """Allow response to be used in boolean context"""
        return self.is_success()
