# ethicrawl/sitemaps/sitemap_result.py
from typing import List
import re
from ethicrawl.core import EthicrawlContext
from ethicrawl.sitemaps.sitemap_urls import SitemapUrlsetUrl


class SitemapResult:
    """Container for sitemap processing results with filtering capabilities."""

    def __init__(self, urls: List[SitemapUrlsetUrl], context: EthicrawlContext):
        self._urls = urls
        self._context = context
        self._logger = context.logger("sitemap.result")

    def filter(self, pattern: str) -> "SitemapResult":
        """Filter URLs by pattern and return a new result object."""
        regex = re.compile(pattern)
        original_count = len(self._urls)
        filtered = [url for url in self._urls if regex.search(url.loc)]
        filtered_count = len(filtered)

        if filtered_count < original_count:
            self._logger.info(
                f"URL filter '{pattern}': {filtered_count}/{original_count} matched"
            )

        return SitemapResult(filtered, self._context)

    @property
    def items(self) -> List[SitemapUrlsetUrl]:
        """Access the URL items directly as a property."""
        return self._urls

    def __iter__(self):
        """Make the result iterable."""
        return iter(self._urls)

    def __len__(self):
        """Support len() function."""
        return len(self._urls)
