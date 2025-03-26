from dataclasses import dataclass, field

from ethicrawl.core import Url

from .base_config import BaseConfig


@dataclass
class HttpProxyConfig(BaseConfig):
    """HTTP proxy configuration settings.

    Manages proxy server URLs for HTTP and HTTPS connections.
    Both proxy types can be configured independently and are validated
    to ensure they contain valid URLs.

    Attributes:
        http: HTTP proxy server URL
        https: HTTPS proxy server URL

    Example:
        >>> from ethicrawl.config import Config
        >>> config = Config()
        >>> # Configure HTTP proxy
        >>> config.http.proxies.http = "http://proxy.example.com:8080"
        >>> # Configure HTTPS proxy
        >>> config.http.proxies.https = "http://secure-proxy.example.com:8443"
        >>> # Clear HTTP proxy
        >>> config.http.proxies.http = None
    """

    _http: Url | None = field(default=None, repr=False)
    _https: Url | None = field(default=None, repr=False)

    def __post_init__(self):
        # Validate initial values
        if self._http is not None:
            self.http = self._http
        if self._https is not None:
            self.https = self._https

    @property
    def http(self) -> Url | None:
        """HTTP proxy server URL.

        Returns:
            Url object or None if not configured
        """
        return self._http

    @http.setter
    def http(self, url: Url | str | None):
        """Set HTTP proxy server URL.

        Args:
            url: Proxy URL as string, Url object, or None to disable

        Raises:
            TypeError: If url is not a string, Url, or None
            ValueError: If url is an invalid URL
        """
        if url is None:
            self._http = None
        elif isinstance(url, Url):
            self._http = Url(url, validate=True)
        elif isinstance(url, str):
            self._http = Url(url, validate=True)
        else:
            raise TypeError(
                f"url must be Url, string, or None, got {type(url).__name__}"
            )

    @property
    def https(self) -> Url | None:
        """HTTPS proxy server URL.

        Returns:
            Url object or None if not configured
        """
        return self._https

    @https.setter
    def https(self, url: Url | str | None):
        """Set HTTPS proxy server URL.

        Args:
            url: Proxy URL as string, Url object, or None to disable

        Raises:
            TypeError: If url is not a string, Url, or None
            ValueError: If url is an invalid URL
        """
        if url is None:
            self._https = None
        elif isinstance(url, Url):
            self._https = Url(url, validate=True)
        elif isinstance(url, str):
            self._https = Url(url, validate=True)
        else:
            raise TypeError(
                f"url must be Url, string, or None, got {type(url).__name__}"
            )

    def to_dict(self) -> dict:
        """Convert proxy configuration to dictionary format.

        Returns:
            Dict with 'http' and 'https' keys mapping to URL strings or None
        """
        return {
            "http": str(self._http) if self._http else None,
            "https": str(self._https) if self._https else None,
        }
