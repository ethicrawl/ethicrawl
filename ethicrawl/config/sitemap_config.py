from dataclasses import dataclass


@dataclass
class SitemapConfig:
    """
    Configuration for sitemap parsing and traversal.

    Controls behavior of sitemap parsing including recursion limits,
    error handling, and filtering options.

    Attributes:
        max_depth (int): Maximum recursion depth for nested sitemaps
        follow_external (bool): Whether to follow sitemap links to external domains
        validate_urls (bool): Whether to validate URLs before adding them to results
        timeout (int): Specific timeout for sitemap requests
    """

    max_depth: int = 5
    follow_external: bool = False
    validate_urls: bool = True
    timeout: int = 30  # Specific timeout for sitemap requests which can be large
