from dataclasses import dataclass, field
from ethicrawl.core.resource import Resource
from typing import Dict
from ethicrawl.config import Config


class Headers(dict):
    """Custom dictionary for HTTP headers that removes keys when value is None"""

    def __setitem__(self, key, value):
        if value is None:
            self.pop(key, None)  # Remove the key if value is None
        else:
            super().__setitem__(key, value)


@dataclass
class HttpRequest(Resource):
    _timeout: float = Config().http.timeout or 30.0
    headers: Dict = field(default_factory=Headers)

    @property
    def timeout(self) -> float:
        """Get the request timeout in seconds."""
        return self._timeout

    @timeout.setter
    def timeout(self, value: float):
        """Set the request timeout with validation."""
        if not isinstance(value, (int, float)):
            raise TypeError("timeout must be a number")
        if value <= 0:
            raise ValueError("timeout must be positive")
        self._timeout = float(value)

    def __post_init__(self):
        super().__post_init__()

        for header, value in Config().http.headers.items():
            self.headers[header] = value

        if not isinstance(self.headers, Headers):
            self.headers = Headers(self.headers)
