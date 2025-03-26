from dataclasses import dataclass, field

from .base_config import BaseConfig


@dataclass
class SitemapConfig(BaseConfig):
    """Configuration for sitemap parsing and traversal.

    Controls behavior of sitemap parsing including recursion limits,
    error handling, and filtering options. This configuration affects
    how sitemaps are discovered, parsed, and which URLs are included
    in the final results.

    Attributes:
        max_depth: Maximum recursion depth for nested sitemaps (default: 5)
        follow_external: Whether to follow sitemap links to external domains (default: False)
        validate_urls: Whether to validate URLs before adding them to results (default: True)

    Example:
        >>> from ethicrawl.config import Config
        >>> config = Config()
        >>> # Increase recursion depth for complex sites
        >>> config.sitemap.max_depth = 10
        >>> # Allow following external domains
        >>> config.sitemap.follow_external = True
    """

    # Private fields for property implementation
    _max_depth: int = field(default=5, repr=False)
    _follow_external: bool = field(default=False, repr=False)
    _validate_urls: bool = field(default=True, repr=False)

    def __post_init__(self):
        # Validate initial values by calling setters
        self.max_depth = self._max_depth
        self.follow_external = self._follow_external
        self.validate_urls = self._validate_urls

    @property
    def max_depth(self) -> int:
        """Maximum recursion depth for nested sitemaps.

        Controls how many levels of sitemap references will be followed.
        Many sites use sitemap indexes that point to other sitemaps, and
        this setting limits how deep that recursion can go.

        Valid range: >= 1
        Default: 5

        Raises:
            TypeError: If value is not an integer
            ValueError: If value is less than 1
        """
        return self._max_depth

    @max_depth.setter
    def max_depth(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"max_depth must be an integer, got {type(value).__name__}")
        if value < 1:
            raise ValueError("max_depth must be at least 1")
        self._max_depth = value

    @property
    def follow_external(self) -> bool:
        """Whether to follow sitemap links to external domains.

        When True, sitemap references to other domains will be followed.
        When False, only sitemaps on the same domain will be processed.

        Default: False

        Raises:
            TypeError: If value is not a boolean
        """
        return self._follow_external

    @follow_external.setter
    def follow_external(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(
                f"follow_external must be a boolean, got {type(value).__name__}"
            )
        self._follow_external = value

    @property
    def validate_urls(self) -> bool:
        """Whether to validate URLs before adding them to results.

        When True, each URL found in sitemaps will be validated for
        proper format before being included in results. This helps
        filter out malformed URLs but adds some processing overhead.

        Default: True

        Raises:
            TypeError: If value is not a boolean
        """
        return self._validate_urls

    @validate_urls.setter
    def validate_urls(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(
                f"validate_urls must be a boolean, got {type(value).__name__}"
            )
        self._validate_urls = value

    def to_dict(self) -> dict:
        """Convert configuration to a dictionary.

        Returns:
            Dictionary with all sitemap configuration values
        """
        return {
            "max_depth": self._max_depth,
            "follow_external": self._follow_external,
            "validate_urls": self._validate_urls,
        }
