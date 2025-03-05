from dataclasses import dataclass
from re import match
from typing import Optional, Union

from ethicrawl.sitemaps.sitemap_util import SitemapHelper


@dataclass
class SitemapIndexUrl:
    """Represents a URL from a sitemap index"""

    loc: str  # REQUIRED: The location URI of a document. The URI must conform to RFC 2396 (http://www.ietf.org/rfc/rfc2396.txt)
    lastmod: Optional[str] = (
        None  # OPTIONAL: The date the document was last modified. The date must conform to the W3C DATETIME format (http://www.w3.org/TR/NOTE-datetime). Example: 2005-05-10 Lastmod may also contain a timestamp. Example: 2005-05-10T17:33:30+08:00
    )

    @staticmethod
    def _validate_url(url: str) -> str:
        """
        Validate and normalize URL.

        Args:
            url: URL string

        Returns:
            str: Normalized URL

        Raises:
            ValueError: If URL is invalid
        """

        if url is None or len(url) == 0:
            raise ValueError("URL cannot be empty")

        # Basic URL validation
        try:
            url = SitemapHelper.validate_url(url)
        except Exception as e:
            raise ValueError(f"Invalid URL format: {str(e)}")

        return url.strip()

    @staticmethod
    def _validate_lastmod(value: Optional[str]) -> Optional[str]:
        """
        Validate lastmod date format.

        Args:
            value: Date string in W3C format

        Returns:
            str: Validated date string

        Raises:
            ValueError: If date format is invalid
        """
        if not value:
            return None

        # Strip whitespace
        value = value.strip()

        # Basic format validation for common patterns
        # Complete W3C datetime validation would be more complex
        date_patterns = [
            r"^\d{4}-\d{2}-\d{2}$",  # YYYY-MM-DD
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([+-]\d{2}:\d{2}|Z)$",  # YYYY-MM-DDThh:mm:ssTZD
        ]

        if not any(match(pattern, value) for pattern in date_patterns):
            raise ValueError(f"Invalid lastmod date format: {value}")

        return value

    def __post_init__(self):
        """
        Validate and normalize all fields after initialization.
        """
        # Validate and normalize URL
        self.loc = SitemapHelper.validate_url(self.loc)

        # Validate lastmod
        self.lastmod = self._validate_lastmod(self.lastmod)

    def __str__(self) -> str:
        """Human-readable string representation"""
        if self.lastmod:
            return f"{self.loc} (last modified: {self.lastmod})"
        return f"{self.loc}"

    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return f"SitemapIndexUrl(loc='{self.loc}', lastmod={repr(self.lastmod)})"


@dataclass
class SitemapUrlsetUrl(SitemapIndexUrl):
    """Represents a URL from a sitemap urlset."""

    changefreq: Optional[str] = (
        None  # OPTIONAL: Indicates how frequently the content at a particular URL is likely to change. The value "always" should be used to describe documents that change each time they are accessed. The value "never" should be used to describe archived URLs. Please note that web crawlers may not necessarily crawl pages marked "always" more often. Consider this element as a friendly suggestion and not a command.
    )
    priority: Optional[float] = (
        None  #  OPTIONAL: The priority of a particular URL relative to other pages on the same site. The value for this element is a number between 0.0 and 1.0 where 0.0 identifies the lowest priority page(s). The default priority of a page is 0.5. Priority is used to select between pages on your site. Setting a priority of 1.0 for all URLs will not help you, as the relative priority of pages on your site is what will be considered.
    )

    _valid_change_freqs = [
        "always",
        "hourly",
        "daily",
        "weekly",
        "monthly",
        "yearly",
        "never",
    ]

    @staticmethod
    def _validate_priority(value: Union[str, float, None]) -> Optional[float]:
        """
        Validate and convert priority value.

        Args:
            value: Priority value as string or float

        Returns:
            float: Normalized priority value

        Raises:
            ValueError: If priority is not between 0.0 and 1.0
        """
        if value is None:
            return None

        # Convert string to float if needed
        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                raise ValueError(f"Priority must be a number, got '{value}'")

        # Validate range
        if not (0.0 <= value <= 1.0):
            raise ValueError(f"Priority must be between 0.0 and 1.0, got {value}")

        return value

    def __post_init__(self):
        """
        Validate and normalize all fields after initialization.
        """
        # Validate and normalize URL
        self.loc = self._validate_url(self.loc)

        # Validate lastmod
        self.lastmod = self._validate_lastmod(self.lastmod)

        # Validate changefreq
        if self.changefreq is not None:
            self.changefreq = self.changefreq.strip().lower()
            if self.changefreq not in self._valid_change_freqs:
                raise ValueError(f"Invalid change frequency: {self.changefreq}")

        # Validate priority
        self.priority = self._validate_priority(self.priority)

    def __str__(self) -> str:
        """Human-readable string representation"""
        parts = [self.loc]

        if self.lastmod:
            parts.append(f"last modified: {self.lastmod}")
        if self.changefreq:
            parts.append(f"frequency: {self.changefreq}")
        if self.priority is not None:
            parts.append(f"priority: {self.priority}")

        return " | ".join(parts)

    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return (
            f"SitemapUrlsetUrl(loc='{self.loc}', lastmod={repr(self.lastmod)}"
            + f"changefreq={repr(self.changefreq)}, priority={repr(self.priority)}"
        )
