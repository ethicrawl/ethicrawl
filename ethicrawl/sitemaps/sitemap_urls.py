from dataclasses import dataclass
from re import match
from typing import Optional, Union
from ethicrawl.core.resource import Resource
from ethicrawl.core.url import Url
from datetime import datetime


@dataclass
class SitemapEntry(Resource):
    """Base class for entries in sitemaps"""

    lastmod: Optional[str] = None

    @staticmethod
    def _validate_lastmod(value: Optional[str]) -> Optional[str]:
        """
        Validate lastmod date format using standard datetime.

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

        # Try standard formats for W3C datetime
        formats = [
            "%Y-%m-%d",  # YYYY-MM-DD
            "%Y-%m-%dT%H:%M:%S",  # YYYY-MM-DDThh:mm:ss
            "%Y-%m-%dT%H:%M:%SZ",  # YYYY-MM-DDThh:mm:ssZ
            "%Y-%m-%dT%H:%M:%S%z",  # YYYY-MM-DDThh:mm:ss+hh:mm (no colon)
            "%Y-%m-%dT%H:%M:%S%:z",  # YYYY-MM-DDThh:mm:ss+hh:mm (with colon)
        ]

        # Try each format
        for fmt in formats:
            try:
                # If parse succeeds, the date is valid
                datetime.strptime(value, fmt)
                return value
            except ValueError:
                continue

        raise ValueError(f"Invalid lastmod date format: {value}")

    def __post_init__(self):
        """Validate fields after initialization."""
        super().__post_init__()  # Call Resource.__post_init__ first
        self.lastmod = self._validate_lastmod(self.lastmod)

    def __str__(self) -> str:
        """Human-readable string representation"""
        if self.lastmod:
            return f"{str(self.url)} (last modified: {self.lastmod})"
        return f"{str(self.url)}"


@dataclass
class SitemapIndexEntry(SitemapEntry):
    """Represents an entry in a sitemap index file"""

    # Index entries only have loc (url) and lastmod, which are inherited

    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return f"SitemapIndexEntry(url='{str(self.url)}', lastmod={repr(self.lastmod)})"


@dataclass
class SitemapUrlsetEntry(SitemapEntry):
    """Represents an entry in a sitemap urlset file"""

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
        """Validate fields after initialization."""
        super().__post_init__()  # Call parent's validation

        # Validate changefreq
        if self.changefreq is not None:
            self.changefreq = self.changefreq.strip().lower()
            if self.changefreq not in self._valid_change_freqs:
                raise ValueError(f"Invalid change frequency: {self.changefreq}")

        # Validate priority
        self.priority = self._validate_priority(self.priority)

    def __str__(self) -> str:
        """Human-readable string representation"""
        parts = [str(self.url)]

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
            f"SitemapUrlsetEntry(url='{str(self.url)}', lastmod={repr(self.lastmod)}, "
            f"changefreq={repr(self.changefreq)}, priority={repr(self.priority)})"
        )
