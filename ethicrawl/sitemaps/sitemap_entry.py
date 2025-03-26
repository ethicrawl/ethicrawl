from dataclasses import dataclass
from datetime import datetime

from ethicrawl.core.resource import Resource


@dataclass
class SitemapEntry(Resource):
    """Base class for entries found in XML sitemaps.

    SitemapEntry extends Resource to represent entries from XML sitemaps with
    their additional metadata. It maintains the URL identity pattern while
    adding sitemap-specific attributes like the last modification date.

    This class handles validation of W3C datetime formats and provides
    appropriate string representation of sitemap entries.

    Attributes:
        url: URL of the sitemap entry (inherited from Resource)
        lastmod: Last modification date string in W3C format (optional)

    Example:
        >>> from ethicrawl.core import Url
        >>> from ethicrawl.sitemaps import SitemapEntry
        >>> entry = SitemapEntry(
        ...     Url("https://example.com/page1"),
        ...     lastmod="2023-06-15T14:30:00Z"
        ... )
        >>> str(entry)
        'https://example.com/page1 (last modified: 2023-06-15T14:30:00Z)'
    """

    lastmod: str | None = None

    @staticmethod
    def _validate_lastmod(value: str | None) -> str | None:
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

        if not isinstance(value, str):
            raise TypeError(f"expected lastmod to be str, got {type(value).__name__}")

        # Strip whitespace
        value = value.strip()

        # Try standard formats for W3C datetime
        formats = [
            "%Y-%m-%d",  # YYYY-MM-DD
            "%Y-%m-%dT%H:%M:%S",  # YYYY-MM-DDThh:mm:ss
            "%Y-%m-%dT%H:%M:%SZ",  # YYYY-MM-DDThh:mm:ssZ
            "%Y-%m-%dT%H:%M:%S%z",  # YYYY-MM-DDThh:mm:ss+hh:mm (no colon)
            "%Y-%m-%dT%H:%M:%S%:z",  # YYYY-MM-DDThh:mm:ss+hh:mm (with colon)
            "%Y-%m-%dT%H:%M:%S.%fZ",  # YYYY-MM-DDThh:mm:ss.ssssssZ (with microseconds)
            "%Y-%m-%dT%H:%M:%S.%f",  # YYYY-MM-DDThh:mm:ss.ssssss (with microseconds, no Z)
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
        """Validate fields after initialization.

        Validates the lastmod date format if provided, ensuring it
        conforms to one of the accepted W3C datetime formats.

        Raises:
            ValueError: If lastmod format is invalid
            TypeError: If lastmod is not a string
        """
        super().__post_init__()  # Call Resource.__post_init__ first
        self.lastmod = self._validate_lastmod(self.lastmod)

    def __str__(self) -> str:
        """Human-readable string representation of the sitemap entry.

        Returns:
            URL string with last modification date if available
        """
        if self.lastmod:
            return f"{str(self.url)} (last modified: {self.lastmod})"
        return f"{str(self.url)}"
