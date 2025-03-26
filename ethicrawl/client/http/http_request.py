from dataclasses import dataclass, field

from ethicrawl.config import Config, HttpConfig
from ethicrawl.core import Headers
from ethicrawl.client import Request


@dataclass
class HttpRequest(Request):
    """HTTP-specific request implementation with timeout and header management.

    This class extends the base Request with HTTP-specific functionality,
    including configurable timeout and header handling. It automatically applies
    default headers from the global configuration while allowing custom headers
    to take precedence.

    Attributes:
        url: The target URL (inherited from Request)
        headers: HTTP headers to send with the request
        _timeout: Request timeout in seconds

    Example:
        >>> from ethicrawl.client.http import HttpRequest
        >>> from ethicrawl.core import Url
        >>> req = HttpRequest(Url("https://example.com"))
        >>> req.headers["User-Agent"] = "EthiCrawl/1.0"
        >>> req.timeout = 15.0
    """

    _timeout: float = Config().http.timeout or 30.0
    headers: Headers = field(default_factory=Headers)

    @property
    def timeout(self) -> float:
        """Get the request timeout in seconds.

        Returns:
            The timeout value in seconds
        """
        return self._timeout

    @timeout.setter
    def timeout(self, value: float):
        """Set the request timeout with validation.

        Args:
            value: The new timeout value in seconds

        Raises:
            ValueError: If the timeout is negative or otherwise invalid
        """
        temp_config = HttpConfig()
        # This will raise the appropriate exceptions if invalid
        temp_config.timeout = value
        # If we get here, the value passed validation
        self._timeout = float(value)

    def __post_init__(self):
        """Initialize and validate the request after creation.

        Ensures headers are a proper Headers instance and applies
        default headers from configuration if not already present.
        """
        super().__post_init__()

        # Ensure self.headers is a Headers instance
        if not isinstance(self.headers, Headers):
            self.headers = Headers(self.headers)

        # Apply Config headers, NOT overriding existing ones
        for header, value in Config().http.headers.items():
            if header not in self.headers:
                self.headers[header] = value
