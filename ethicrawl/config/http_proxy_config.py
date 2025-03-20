from dataclasses import dataclass, field
from typing import Optional, Union

from ethicrawl.core import Url

from .base_config import BaseConfig


@dataclass
class HttpProxyConfig(BaseConfig):
    _http: Optional[Url] = field(default=None, repr=False)
    _https: Optional[Url] = field(default=None, repr=False)

    def __post_init__(self):
        # Validate initial values
        if self._http is not None:
            self.http = self._http
        if self._https is not None:
            self.https = self._https

    @property
    def http(self) -> Optional[Url]:
        return self._http

    @http.setter
    def http(self, url: Union[Url, str, None]):
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
    def https(self) -> Optional[Url]:
        return self._https

    @https.setter
    def https(self, url: Union[Url, str, None]):
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
        """Convert config to dictionary."""
        return {
            "http": str(self._http) if self._http else None,
            "https": str(self._https) if self._https else None,
        }
