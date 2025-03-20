"""Sitemap parsing and handling."""

from .index_entry import IndexEntry
from .index_node import IndexNode
from .sitemap_entry import SitemapEntry
from .sitemap_node import SitemapNode
from .sitemap_parser import SitemapParser
from .urlset_entry import UrlsetEntry
from .urlset_node import UrlsetNode

URLSET = "urlset"
SITEMAPINDEX = "sitemapindex"


__all__ = [
    "IndexEntry",
    "IndexNode",
    "SitemapEntry",
    "SitemapNode",
    "SitemapParser",
    "SitemapType",
    "UrlsetEntry",
    "UrlsetNode",
]
