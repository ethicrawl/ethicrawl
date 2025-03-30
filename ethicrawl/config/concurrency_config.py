from dataclasses import dataclass, field

from .base_config import BaseConfig


@dataclass
class ConcurrencyConfig(BaseConfig):
    """Configuration for asynchronous operations."""

    # Private fields for property implementation
    _enabled: bool = field(default=False, repr=False)
    _requests: int = field(default=1, repr=False)  # 1 = single thread by default
    _chrome: int = field(default=-1, repr=False)  # -1 = disabled by default

    def __post_init__(self):
        # Validate initial values by calling setters
        self.enabled = self._enabled
        self.requests = self._requests
        self.chrome = self._chrome

    @property
    def enabled(self) -> bool:
        """Whether asynchronous operation is enabled.

        When True, ethicrawl will use async operations when available.
        When False, all operations will be synchronous.

        Default: False

        Raises:
            TypeError: If value is not a boolean
        """
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(f"enabled must be a boolean, got {type(value).__name__}")
        self._enabled = value

    @property
    def requests(self) -> int:
        """Maximum number of concurrent HTTP requests using the RequestsTransport

        Controls how many HTTP requests can be in flight simultaneously.
        Higher values increase throughput but also server load.

        Valid values:
        - -1: Use synchronous operation fallback (disable multithreading)
        - 0: No RequestsTransport threads at all; requests will fail with this transport
        - 1+: Number of additional threads to create

        Note: Always returns -1 when enabled=False, regardless of stored value.

        Default: 1

        Raises:
            TypeError: If value is not an integer
            ValueError: If value is less than -1
        """
        # Force synchronous operation when async is disabled
        if not self._enabled:
            return -1
        return self._requests

    @requests.setter
    def requests(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"requests must be an integer, got {type(value).__name__}")
        if value < -1:
            raise ValueError("requests must be -1 or greater")
        self._requests = value

    @property
    def chrome(self) -> int:
        """Number of concurrent HTTP requests using the ChromeTransports

        Controls how many Chrome instances can run simultaneously for
        rendering JavaScript-heavy pages.

        Valid values:
        - -1: Use synchronous operation fallback (disable multithreading)
        - 0: No ChromeTransport threads at all; requests will fail with this transport
        - 1+: Number of additional Chrome instances to create

        Note: Always returns -1 when enabled=False, regardless of stored value.

        Default: -1 (disabled)

        Raises:
            TypeError: If value is not an integer
            ValueError: If value is less than -1
        """
        # Force synchronous operation when async is disabled
        if not self._enabled:
            return -1
        return self._chrome

    @chrome.setter
    def chrome(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"chrome must be an integer, got {type(value).__name__}")
        if value < -1:
            raise ValueError("chrome must be -1 or greater")
        self._chrome = value

    def to_dict(self) -> dict:
        """Convert configuration to a dictionary.

        Returns:
            Dictionary with all async configuration values
        """
        return {
            "enabled": self._enabled,
            "requests": self._requests,
            "chrome": self._chrome,
        }
