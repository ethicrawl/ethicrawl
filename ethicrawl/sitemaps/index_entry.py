from dataclasses import dataclass

from .sitemap_entry import SitemapEntry


@dataclass
class IndexEntry(SitemapEntry):
    """Represents an entry in a sitemap index file"""

    # Index entries only have loc (url) and lastmod, which are inherited

    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return f"SitemapIndexEntry(url='{str(self.url)}', lastmod={repr(self.lastmod)})"
