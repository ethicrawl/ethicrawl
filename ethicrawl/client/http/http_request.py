# FIXME: remove comment, imports sorted

from dataclasses import dataclass, field
from typing import Dict

from ethicrawl.config import Config, HttpConfig
from ethicrawl.core import Headers, Resource


@dataclass
class HttpRequest(Resource):
    _timeout: float = Config().http.timeout or 30.0
    headers: Headers = field(default_factory=Headers)

    @property
    def timeout(self) -> float:
        """Get the request timeout in seconds."""
        return self._timeout

    @timeout.setter
    def timeout(self, value: float):
        """Set the request timeout with validation."""
        temp_config = HttpConfig()
        # This will raise the appropriate exceptions if invalid
        temp_config.timeout = value
        # If we get here, the value passed validation
        self._timeout = float(value)

    def __post_init__(self):
        super().__post_init__()

        # Ensure self.headers is a Headers instance
        if not isinstance(self.headers, Headers):
            self.headers = Headers(self.headers)

        # Apply Config headers, NOT overriding existing ones
        for header, value in Config().http.headers.items():
            if header not in self.headers:
                self.headers[header] = value
