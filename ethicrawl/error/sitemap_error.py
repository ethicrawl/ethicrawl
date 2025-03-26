from .ethicrawl_error import EthicrawlError


class SitemapError(EthicrawlError):
    """Raised when a sitemap cannot be parsed or processed.

    This exception indicates problems with sitemap fetching, parsing,
    or validation, such as invalid XML or missing required elements.
    """
