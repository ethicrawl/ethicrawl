from dataclasses import dataclass, field
from typing import Optional, Union

from ethicrawl.core import Headers

from .base_config import BaseConfig
from .http_proxy_config import HttpProxyConfig


@dataclass
class HttpConfig(BaseConfig):
    """HTTP client configuration"""

    # Private fields for property implementation
    _timeout: float = field(default=30.0, repr=False)
    _max_retries: int = field(default=3, repr=False)
    _retry_delay: float = field(default=1.0, repr=False)
    _rate_limit: Optional[float] = field(default=0.5, repr=False)
    _jitter: float = field(default=0.2, repr=False)
    _user_agent: str = field(default="Ethicrawl/1.0", repr=False)
    _headers: Headers[str, str] = field(default_factory=Headers, repr=False)
    _proxies: HttpProxyConfig = field(default_factory=HttpProxyConfig, repr=False)

    def __post_init__(self):
        # Validate initial values by calling setters
        # This ensures values provided at instantiation are also validated
        self.timeout = self._timeout
        self.max_retries = self._max_retries
        self.retry_delay = self._retry_delay
        self.rate_limit = self._rate_limit
        self.jitter = self._jitter
        self.user_agent = self._user_agent

    @property
    def timeout(self) -> float:
        """Request timeout in seconds"""
        return self._timeout

    @timeout.setter
    def timeout(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError(f"timeout must be a number, got {type(value).__name__}")
        if value <= 0:
            raise ValueError("timeout must be positive")
        if value > 300:
            raise ValueError("maximum timeout is 300 seconds")
        self._timeout = float(value)

    @property
    def max_retries(self) -> int:
        """Maximum number of retry attempts"""
        return self._max_retries

    @max_retries.setter
    def max_retries(self, value: int):
        if not isinstance(value, int):
            raise TypeError(
                f"max_retries must be an integer, got {type(value).__name__}"
            )
        if value < 0:
            raise ValueError("max_retries cannot be negative")
        if value > 10:
            raise ValueError("max_retries cannot be more than 10")
        self._max_retries = value

    @property
    def retry_delay(self) -> float:
        """Base delay between retries in seconds"""
        return self._retry_delay

    @retry_delay.setter
    def retry_delay(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError(f"retry_delay must be a number, got {type(value).__name__}")
        if value < 0:
            raise ValueError("retry_delay cannot be negative")
        if value > 60:
            raise ValueError("retry_delay cannot be more than 60")
        self._retry_delay = float(value)

    @property
    def rate_limit(self) -> Optional[float]:
        """Requests per second (None=unlimited)"""
        return self._rate_limit

    @rate_limit.setter
    def rate_limit(self, value: Optional[float]):
        if not isinstance(value, (int, float)):
            raise TypeError(f"rate_limit must be a number, got {type(value).__name__}")
        if value <= 0:
            raise ValueError("rate_limit must be positive")
        self._rate_limit = float(value)

    @property
    def jitter(self) -> float:
        """Random jitter factor for rate limiting"""
        return self._jitter

    @jitter.setter
    def jitter(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError(f"jitter must be a number, got {type(value).__name__}")
        if value < 0 or value >= 1:
            raise ValueError("jitter must be between 0.0 and 1.0")
        self._jitter = float(value)

    @property
    def user_agent(self) -> str:
        """User agent string"""
        return self._user_agent

    @user_agent.setter
    def user_agent(self, value: str):
        if not isinstance(value, str):
            raise TypeError(f"user_agent must be a string, got {type(value).__name__}")
        if not value.strip():
            raise ValueError("user_agent cannot be empty")
        self._user_agent = value

    @property
    def headers(self) -> Headers:
        """Get request headers."""
        return self._headers

    @headers.setter
    def headers(self, value: Union[Headers, dict]):
        """Set request headers."""
        if isinstance(value, Headers):
            self._headers = value.copy()
        elif isinstance(value, dict):
            # Let the Headers constructor handle validation
            self._headers = Headers(value)
        else:
            raise TypeError(
                f"headers must be a Headers instance or dictionary, got {type(value).__name__}"
            )

    @property
    def proxies(self) -> HttpProxyConfig:
        """Get proxy configuration."""
        return self._proxies

    @proxies.setter
    def proxies(self, value: Union[HttpProxyConfig, dict]):
        """Set proxy configuration."""
        if isinstance(value, HttpProxyConfig):
            self._proxies = value
        elif isinstance(value, dict):
            # Create a new proxy config instance
            proxy_config = HttpProxyConfig()

            # Set the http and https values if present
            if "http" in value:
                proxy_config.http = value["http"]
            if "https" in value:
                proxy_config.https = value["https"]

            self._proxies = proxy_config
        else:
            raise TypeError(
                f"proxies must be a HttpProxyConfig instance or dictionary, got {type(value).__name__}"
            )

    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "timeout": self._timeout,
            "rate_limit": self._rate_limit,
            "jitter": self._jitter,
            "max_retries": self._max_retries,
            "retry_delay": self._retry_delay,
            "user_agent": self._user_agent,
            "headers": self._headers,
            "proxies": self._proxies.to_dict(),
        }
