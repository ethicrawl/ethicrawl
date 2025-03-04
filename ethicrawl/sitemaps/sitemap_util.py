from enum import Enum
from urllib.parse import urlparse
from re import sub


class SitemapType(Enum):
    """Enum for the two possible sitemap types."""

    INDEX = "sitemapindex"
    URLSET = "urlset"
    UNDEFINED = "undefined"


class SitemapError(Exception):
    """Exception raised for sitemap parsing errors."""

    pass


class SitemapHelper:
    """Helper class with utility methods for sitemap processing."""

    @staticmethod
    def validate_url(url: str) -> str:
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
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                raise ValueError(f"URL must include scheme and domain: {url}")
        except Exception as e:
            raise ValueError(f"Invalid URL format: {str(e)}")

        return url.strip()

    @staticmethod
    def escape_unescaped_ampersands(xml_document: str) -> str:
        """Escape unescaped ampersands in XML content."""
        pattern = r"&(?!(?:[a-zA-Z]+|#[0-9]+|#x[0-9a-fA-F]+);)"
        return sub(pattern, "&amp;", xml_document)
