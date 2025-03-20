from dataclasses import dataclass

from .sitemap_entry import SitemapEntry


@dataclass
class UrlsetEntry(SitemapEntry):
    """Represents an entry in a sitemap urlset file"""

    changefreq: str | None = None
    priority: float | str | None = None

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
    def _validate_priority(
        value: str | float | int | None = None,
    ) -> float | None:
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
                raise TypeError(
                    f"Priority must be a number, got '{type(value).__name__}'"
                )

        # Always convert to float (handles integers)
        value = float(value)

        # Validate range
        if not (0.0 <= value <= 1.0):
            raise ValueError(f"Priority must be between 0.0 and 1.0, got {value}")

        return value

    @staticmethod
    def _validate_changefreq(value: str | None) -> str | None:
    def _validate_changefreq(
        value: Optional[str],
    ) -> Optional[str]:
        """
        Validate and normalize change frequency value.

        Args:
            value: Change frequency string or None

        Returns:
            str: Normalized change frequency (lowercase, stripped) or None

        Raises:
            TypeError: If changefreq is not a string
            ValueError: If changefreq is not one of the valid values
        """
        if value is None:
            return None

        if not isinstance(value, str):
            raise TypeError(f"changefreq must be a string, got {type(value).__name__}")

        # Normalize: strip and lowercase
        normalized = value.strip().lower()

        # Validate against valid frequencies
        valid_freqs = [
            "always",
            "hourly",
            "daily",
            "weekly",
            "monthly",
            "yearly",
            "never",
        ]

        if normalized not in valid_freqs:
            raise ValueError(
                f"Invalid change frequency: '{value}'. Must be one of: {', '.join(valid_freqs)}"
            )

        return normalized

    def __post_init__(self):
        """Validate fields after initialization."""
        super().__post_init__()  # Call parent's validation

        # Validate changefreq
        if self.changefreq is not None:
            self.changefreq = self._validate_changefreq(self.changefreq)

        # Validate priority
        if self.priority is not None:
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
