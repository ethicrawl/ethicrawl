from typing import List

from lxml import etree

from ethicrawl.context import Context
from ethicrawl.core import Url

from .const import URLSET
from .index_entry import IndexEntry
from .urlset_entry import UrlsetEntry

from .sitemap_node import SitemapNode


class UrlsetNode(SitemapNode):
    def __init__(self, context: Context, document: str = None) -> None:
        super().__init__(context, document)
        if document is not None:
            _localname = etree.QName(self._root.tag).localname
            if _localname != URLSET:
                raise ValueError(f"Expected a root {URLSET} got {_localname}")
            self._entries = self._parse_urlset_sitemap(document)

    def _parse_urlset_sitemap(self, document) -> List[IndexEntry]:
        """Parse sitemap references from a sitemap index."""
        urlset = []

        nsmap = {None: self.SITEMAP_NS}
        _root = etree.fromstring(document.encode("utf-8"), parser=self._parser)

        # Find all sitemap elements
        for url_elem in _root.findall(".//url", namespaces=nsmap):
            try:
                loc_elem = url_elem.find("loc", namespaces=nsmap)
                if loc_elem is None or not loc_elem.text:
                    continue

                # Get optional elements
                lastmod_elem = url_elem.find("lastmod", namespaces=nsmap)
                changefreq_elem = url_elem.find("changefreq", namespaces=nsmap)
                priority_elem = url_elem.find("priority", namespaces=nsmap)

                # Create UrlsetEntry object - validation happens in __post_init__
                url = UrlsetEntry(
                    url=Url(loc_elem.text),
                    lastmod=lastmod_elem.text if lastmod_elem is not None else None,
                    changefreq=(
                        changefreq_elem.text if changefreq_elem is not None else None
                    ),
                    priority=priority_elem.text if priority_elem is not None else None,
                )

                urlset.append(url)
            except ValueError as e:  # pragma: no cover
                self._logger.warning(f"Error parsing sitemap reference: {e}")
        return urlset
