from dataclasses import dataclass

from .sitemap_entry import SitemapEntry


@dataclass
class IndexEntry(SitemapEntry):
    """Represents an entry in a sitemap index file.

    IndexEntry specializes SitemapEntry for use in sitemap index files.
    Sitemap indexes are XML files that contain references to other sitemap
    files, allowing websites to organize their sitemaps hierarchically.

    IndexEntry maintains the same attributes as SitemapEntry (url and lastmod)
    but provides specialized string representation appropriate for index entries.

    Attributes:
        url: URL of the sitemap file (inherited from Resource)
        lastmod: Last modification date of the sitemap (inherited from SitemapEntry)

    Example:
        >>> from ethicrawl.core import Url
        >>> from ethicrawl.sitemaps import IndexEntry
        >>> index = IndexEntry(
        ...     Url("https://example.com/sitemap-products.xml"),
        ...     lastmod="2023-06-15T14:30:00Z"
        ... )
        >>> str(index)
        'https://example.com/sitemap-products.xml (last modified: 2023-06-15T14:30:00Z)'
        >>> repr(index)
        "SitemapIndexEntry(url='https://example.com/sitemap-products.xml', lastmod='2023-06-15T14:30:00Z')"
    """

    def __repr__(self) -> str:
        """Detailed representation for debugging.

        Returns:
            String representation showing class name and field values
        """
        return f"SitemapIndexEntry(url='{str(self.url)}', lastmod={repr(self.lastmod)})"
