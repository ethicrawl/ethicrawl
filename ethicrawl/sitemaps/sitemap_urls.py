from dataclasses import dataclass
from re import match
from typing import Optional, Union
from ethicrawl.core.url import Url


@dataclass
class SitemapIndexUrl:
    """Represents a URL from a sitemap index"""

    loc: Url  # REQUIRED: The location URI of a document
    lastmod: Optional[str] = (
        None  # OPTIONAL: W3C DATETIME format date the document was last modified
    )

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
        # Validate lastmod
        self.lastmod = self._validate_lastmod(self.lastmod)

    def __str__(self) -> str:
        """Human-readable string representation"""
        if self.lastmod:
            return f"{str(self.loc)} (last modified: {self.lastmod})"
        return f"{str(self.loc)}"

    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return f"SitemapIndexUrl(loc='{str(self.loc)}', lastmod={repr(self.lastmod)})"


@dataclass
class SitemapUrlsetUrl(SitemapIndexUrl):
    """Represents a URL from a sitemap urlset."""

    changefreq: Optional[str] = None  # OPTIONAL: How frequently the content changes
    priority: Optional[float] = (
        None  # OPTIONAL: Priority relative to other pages (0.0-1.0)
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
        # Call parent's validation (handles URL conversion and lastmod validation)
        super().__post_init__()

        # Validate changefreq
        if self.changefreq is not None:
            self.changefreq = self.changefreq.strip().lower()
            if self.changefreq not in self._valid_change_freqs:
                raise ValueError(f"Invalid change frequency: {self.changefreq}")

        # Validate priority
        self.priority = self._validate_priority(self.priority)

    def __str__(self) -> str:
        """Human-readable string representation"""
        parts = [str(self.loc)]

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
            f"SitemapUrlsetUrl(loc='{str(self.loc)}', lastmod={repr(self.lastmod)}, "
            f"changefreq={repr(self.changefreq)}, priority={repr(self.priority)})"
        )
