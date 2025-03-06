from ethicrawl.client import HttpClient
from typing import Optional
import urllib.parse
from ethicrawl.logger import Logger


class EthicrawlContext:
    def __init__(self, url: str, http_client: Optional[HttpClient] = None):
        self._url = self._validate_and_normalize_url(url)
        self._client = self._validate_client(http_client)  # Can be None
        self._logger = Logger.logger(self._url, "core")

    def _validate_and_normalize_url(self, url: str) -> str:
        """Validate URL and normalize to base URL (protocol + domain)."""
        if not isinstance(url, str):
            raise ValueError(f"URL must be a string, got {type(url)}")

        # Parse URL into components
        parsed = urllib.parse.urlparse(url)

        # Check that we have the minimum required components
        if not (parsed.scheme and parsed.netloc):
            raise ValueError(f"URL must contain protocol and domain: {url}")

        # Normalize to base URL (protocol + domain)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        return base_url

    def _validate_client(self, client: Optional[HttpClient]) -> Optional[HttpClient]:
        """Validate client is either None or an HttpClient instance."""
        if client is None:
            return None

        if not isinstance(client, HttpClient):
            raise ValueError(
                f"client must be an HttpClient instance or None, got {type(client)}"
            )
        return client

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, url: str):
        self._url = self._validate_and_normalize_url(url)

    @property
    def client(self) -> Optional[HttpClient]:
        return self._client

    @client.setter
    def client(self, client: Optional[HttpClient]):
        self._client = self._validate_client(client)

    def get_logger(self, component: str):
        """Get a component-specific logger within this context."""
        return Logger.logger(self._url, component)

    def __str__(self) -> str:
        """Return a human-readable string representation of the context."""
        client_status = "with client" if self._client else "without client"
        return f"EthicrawlContext({self._url}, {client_status})"

    def __repr__(self) -> str:
        """Return an unambiguous string representation of the context."""
        client_repr = f"client={repr(self._client)}" if self._client else "client=None"
        return f"EthicrawlContext(url='{self._url}', {client_repr})"
