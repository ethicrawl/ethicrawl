from typing import Dict, Any, Optional


class HttpResponse:
    """
    Standardized HTTP response object that's independent of the underlying HTTP library.
    """

    def __init__(
        self, status_code: int, text: str, headers: Dict = None, content: bytes = None
    ):
        self.status_code = status_code
        self.text = text
        self.headers = headers or {}
        self.content = content

    def is_success(self) -> bool:
        """Check if the response indicates success (2xx status code)"""
        return 200 <= self.status_code < 300

    def __bool__(self):
        """Allow response to be used in boolean context"""
        return self.is_success()
