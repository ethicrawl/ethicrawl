# from ethicrawl.client import HttpClient
from typing import Optional, TYPE_CHECKING, Any
import urllib.parse
from ethicrawl.logger import Logger
from ethicrawl.core.url import Url

if TYPE_CHECKING:
    from ethicrawl.client import HttpClient


class Context:
    def __init__(self, url: Url, http_client: Optional["HttpClient"] = None) -> None:
        self._url = Url(str(url))
        self._client = None
        if http_client is not None:
            self._client = self._validate_client(http_client)
        self._logger = Logger.logger(self._url, "core")

    def _validate_client(
        self, client: Any
    ) -> Optional["HttpClient"]:  # Use Any for runtime
        """Validate client is either None or an HttpClient instance."""
        if client is None:
            return None
        from ethicrawl.client import HttpClient

        if not isinstance(client, HttpClient):
            raise ValueError(
                f"client must be an HttpClient instance or None, got {type(client)}"
            )
        return client

    @property
    def url(self) -> Url:
        return self._url

    @url.setter
    def url(self, url: str):
        self._url = Url(url)

    @property
    def client(self) -> Optional["HttpClient"]:
        return self._client

    @client.setter
    def client(self, client: Optional["HttpClient"]):
        self._client = self._validate_client(client)

    def logger(self, component: str):
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
