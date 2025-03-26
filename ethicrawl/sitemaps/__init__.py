"""XML sitemap parsing and traversal for discovering website structure."""

from .index_entry import IndexEntry
from .index_document import IndexDocument
from .sitemap_entry import SitemapEntry
from .sitemap_document import SitemapDocument
from .sitemap_parser import SitemapParser
from .urlset_entry import UrlsetEntry
from .urlset_document import UrlsetDocument

URLSET = "urlset"
SITEMAPINDEX = "sitemapindex"


__all__ = [
    "IndexEntry",
    "IndexDocument",
    "SitemapEntry",
    "SitemapDocument",
    "SitemapParser",
    "UrlsetEntry",
    "UrlsetDocument",
]
