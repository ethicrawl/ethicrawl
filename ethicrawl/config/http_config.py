from dataclasses import dataclass, field

from ethicrawl.core import Headers

from .base_config import BaseConfig
from .http_proxy_config import HttpProxyConfig


@dataclass
class HttpConfig(BaseConfig):
    """HTTP client configuration settings for Ethicrawl.

    This class manages all HTTP-specific configuration options including
    timeouts, rate limiting, retries, user agent settings, headers, and
    proxy configuration. It provides validation for all values to ensure
    they're within safe and reasonable ranges.

    All setters perform type checking and value validation to prevent
    invalid configurations. The class integrates with the global Config
    singleton for system-wide settings.

    Attributes:
        timeout: Request timeout in seconds (default: 30.0)
        max_retries: Maximum retry attempts for failed requests (default: 3)
        retry_delay: Base delay between retries in seconds (default: 1.0)
        rate_limit: Maximum requests per second (default: 0.5)
        jitter: Random variation factor for rate limiting (default: 0.2)
        user_agent: User agent string for requests (default: "Ethicrawl/1.0")
        headers: Default headers to include with requests
        proxies: Proxy server configuration

    Example:
        >>> from ethicrawl.config import Config
        >>> # Get the global configuration
        >>> config = Config()
        >>> # Update HTTP settings
        >>> config.http.timeout = 60.0
        >>> config.http.user_agent = "MyCustomCrawler/2.0"
        >>> config.http.rate_limit = 1.0  # 1 request per second
        >>> # Configure proxy
        >>> config.http.proxies = {"http": "http://proxy:8080", "https": "https://proxy:8443"}
    """

    # Private fields for property implementation
    _timeout: float = field(default=30.0, repr=False)
    _max_retries: int = field(default=3, repr=False)
    _retry_delay: float = field(default=1.0, repr=False)
    _rate_limit: float | None = field(default=0.5, repr=False)
    _jitter: float = field(default=0.2, repr=False)
    _user_agent: str = field(default="Ethicrawl/1.0", repr=False)
    _headers: Headers = field(default_factory=Headers, repr=False)
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
        """Request timeout in seconds.

        Controls how long to wait for a response before abandoning the request.

        Valid range: 0 < timeout <= 300
        Default: 30.0

        Raises:
            TypeError: If value is not a number
            ValueError: If value is <= 0 or > 300
        """
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
        """Maximum number of retry attempts for failed requests.

        Controls how many times a failed request should be retried
        before giving up. Uses exponential backoff between attempts.

        Valid range: 0-10 (0 means no retries)
        Default: 3

        Raises:
            TypeError: If value is not an integer
            ValueError: If value is negative or > 10
        """
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
    def rate_limit(self) -> float | None:
        """Maximum requests per second allowed.

        Controls request frequency to avoid overwhelming servers.
        Set to None to disable rate limiting (not recommended).

        Example: 0.5 means maximum of one request every 2 seconds

        Valid range: > 0
        Default: 0.5

        Raises:
            TypeError: If value is not a number
            ValueError: If value is <= 0
        """
        return self._rate_limit

    @rate_limit.setter
    def rate_limit(self, value: float | None):
        if not isinstance(value, (int, float)):
            raise TypeError(f"rate_limit must be a number, got {type(value).__name__}")
        if value <= 0:
            raise ValueError("rate_limit must be positive")
        self._rate_limit = float(value)

    @property
    def jitter(self) -> float:
        """Random variation factor for rate limiting.

        Adds randomness to the timing between requests to make
        crawling patterns less predictable. The random factor
        is calculated as: delay * (1 + random() * jitter)

        Valid range: 0.0-1.0
        Default: 0.2

        Raises:
            TypeError: If value is not a number
            ValueError: If value outside allowed range
        """
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
    def headers(self, value: Headers | dict):
        """Set request headers."""
        if isinstance(value, Headers):
            self._headers = value
        elif isinstance(value, dict):
            # Let the Headers constructor handle validation
            self._headers = Headers(value)
        else:
            raise TypeError(
                f"headers must be a Headers instance or dictionary, got {type(value).__name__}"
            )

    @property
    def proxies(self) -> HttpProxyConfig:
        """Proxy server configuration for HTTP requests.

        Configures HTTP and HTTPS proxy servers for requests.

        Example:
            >>> config.http.proxies = {
            ...    "http": "http://proxy:8080",
            ...    "https": "https://proxy:8443"
            ... }

        Returns:
            HttpProxyConfig object with http and https properties

        Raises:
            TypeError: If value is not HttpProxyConfig or dict
        """
        return self._proxies

    @proxies.setter
    def proxies(self, value: HttpProxyConfig | dict):
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
