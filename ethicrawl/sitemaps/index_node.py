
from lxml import etree

from ethicrawl.context import Context
from ethicrawl.core import Url

from .const import SITEMAPINDEX
from .index_entry import IndexEntry
from .sitemap_node import SitemapNode


class IndexNode(SitemapNode):
    def __init__(self, context: Context, document: str | None = None) -> None:
        super().__init__(context, document)
        if document is not None:
            _localname = etree.QName(self._root.tag).localname
            if _localname != SITEMAPINDEX:
                raise ValueError(
                    f"Expected a root {SITEMAPINDEX} got {_localname}")
            self._entries = self._parse_index_sitemap(document)

    def _parse_index_sitemap(self, document) -> list[IndexEntry]:
        """Parse sitemap references from a sitemap index."""
        sitemaps = []

        nsmap = {None: self.SITEMAP_NS}
        _root = etree.fromstring(document.encode("utf-8"), parser=self._parser)

        # Find all sitemap elements
        for sitemap_elem in _root.findall(".//sitemap", namespaces=nsmap):
            try:
                # Get the required loc element
                loc_elem = sitemap_elem.find("loc", namespaces=nsmap)
                if loc_elem is None or not loc_elem.text:
                    continue

                # Get optional lastmod element
                lastmod_elem = sitemap_elem.find("lastmod", namespaces=nsmap)

                # Create IndexEntry object (only loc and lastmod)
                index = IndexEntry(
                    url=Url(loc_elem.text),
                    lastmod=lastmod_elem.text if lastmod_elem is not None else None,
                )

                sitemaps.append(index)
            except ValueError as e:  # pragma: no cover
                self._logger.warning(f"Error parsing sitemap reference: {e}")
        return sitemaps

    @property
    def entries(self) -> list[IndexEntry]:
        """Get the sitemaps in this index."""
        return self._entries

    @entries.setter
    def entries(self, entries: list[IndexEntry]) -> None:
        """
        Set the sitemaps in this index.

        Args:
            sitemaps: List of sitemap URLs
        """
        if not isinstance(entries, list):
            raise TypeError(f"Expected a list, got {type(entries).__name__}")

        # Validate all items are of correct type
        for entry in entries:
            if not isinstance(entry, IndexEntry):
                raise TypeError(
                    f"Expected IndexEntry, got {type(entry).__name__}")

        self._entries = entries
