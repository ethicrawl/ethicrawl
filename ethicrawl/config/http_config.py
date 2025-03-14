from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass
class HttpConfig:
    """HTTP client configuration"""

    # Private fields for property implementation
    _timeout: float = field(default=30.0, repr=False)
    _max_retries: int = field(default=3, repr=False)
    _retry_delay: float = field(default=1.0, repr=False)
    _rate_limit: Optional[float] = field(default=0.5, repr=False)
    _jitter: float = field(default=0.2, repr=False)
    _user_agent: str = field(default="Ethicrawl/1.0", repr=False)
    headers: Dict[str, str] = field(default_factory=dict)  # Not using property for this
    _proxies: Dict[str, str] = field(
        default_factory=dict, repr=False
    )  # New proxies attribute

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
            raise TypeError("timeout must be a number")
        if value <= 0:
            raise ValueError("timeout must be positive")
        self._timeout = float(value)

    @property
    def max_retries(self) -> int:
        """Maximum number of retry attempts"""
        return self._max_retries

    @max_retries.setter
    def max_retries(self, value: int):
        if not isinstance(value, int):
            raise TypeError("max_retries must be an integer")
        if value < 0:
            raise ValueError("max_retries cannot be negative")
        self._max_retries = value

    @property
    def retry_delay(self) -> float:
        """Base delay between retries in seconds"""
        return self._retry_delay

    @retry_delay.setter
    def retry_delay(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("retry_delay must be a number")
        if value < 0:
            raise ValueError("retry_delay cannot be negative")
        self._retry_delay = float(value)

    @property
    def rate_limit(self) -> Optional[float]:
        """Requests per second (None=unlimited)"""
        return self._rate_limit

    @rate_limit.setter
    def rate_limit(self, value: Optional[float]):
        if value is not None:
            if not isinstance(value, (int, float)):
                raise TypeError("rate_limit must be a number or None")
            if value <= 0:
                raise ValueError("rate_limit must be positive or None")
            self._rate_limit = float(value)
        else:
            self._rate_limit = None

    @property
    def jitter(self) -> float:
        """Random jitter factor for rate limiting"""
        return self._jitter

    @jitter.setter
    def jitter(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("jitter must be a number")
        if value < 0 or value >= 1:
            raise ValueError("jitter must be between 0 and 1")
        self._jitter = float(value)

    @property
    def user_agent(self) -> str:
        """User agent string"""
        return self._user_agent

    @user_agent.setter
    def user_agent(self, value: str):
        if not isinstance(value, str):
            raise TypeError("user_agent must be a string")
        if not value.strip():
            raise ValueError("user_agent cannot be empty")
        self._user_agent = value

    @property
    def proxies(self) -> dict:
        """Get proxy settings."""
        return self._proxies.copy()

    @proxies.setter
    def proxies(self, value: dict):
        """Set proxy settings."""
        if not isinstance(value, dict):
            raise TypeError("Proxies must be a dictionary")
        self._proxies = value.copy()

    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "timeout": self._timeout,
            "rate_limit": self._rate_limit,
            "jitter": self._jitter,
            "max_retries": self._max_retries,
            "retry_delay": self._retry_delay,
            "user_agent": self._user_agent,
            "headers": self.headers,
            "proxies": self._proxies,
        }

    # Convenience methods for common proxy configurations
    def set_http_proxy(self, proxy_url: str):
        """Set HTTP proxy."""
        self._proxies["http"] = proxy_url

    def set_https_proxy(self, proxy_url: str):
        """Set HTTPS proxy."""
        self._proxies["https"] = proxy_url

    def set_all_proxies(self, proxy_url: str):
        """Set proxy for all protocols."""
        self._proxies["http"] = proxy_url
        self._proxies["https"] = proxy_url
