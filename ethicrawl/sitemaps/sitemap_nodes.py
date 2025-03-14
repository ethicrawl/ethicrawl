from typing import List


from lxml import etree

# import lxml
# import lxml.etree


from ethicrawl.sitemaps.sitemap_entries import IndexEntry, UrlsetEntry
from ethicrawl.sitemaps.sitemap_util import SitemapError, SitemapHelper, SitemapType

from ethicrawl.core.context import Context
from ethicrawl.core.url import Url


class SitemapNode:
    SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

    def __init__(self, context: Context, document: str = None) -> None:
        self._context = context
        self._logger = self._context.logger("sitemap.node")
        self._entries = []
        self._type = SitemapType.UNDEFINED
        self._parser = etree.XMLParser(
            resolve_entities=False,  # Prevent XXE attacks
            no_network=True,  # Prevent external resource loading
            dtd_validation=False,  # Don't validate DTDs
            load_dtd=False,  # Don't load DTDs at all
            huge_tree=False,  # Prevent XML bomb attacks
        )
        if document is not None:
            self._root = self._validate(document)

    def _validate(self, document: str) -> etree._Element:
        document = SitemapHelper.escape_unescaped_ampersands(
            document
        )  # TODO: might want to move this to the HttpClient
        try:
            _element = etree.fromstring(document.encode("utf-8"), parser=self._parser)
            if _element.nsmap[None] != SitemapNode.SITEMAP_NS:
                self._logger.error(
                    f"Required default namespace not found: {SitemapNode.SITEMAP_NS}"
                )
                raise SitemapError(
                    f"Required default namespace not found: {SitemapNode.SITEMAP_NS}"
                )
            try:
                _ = etree.QName(_element.tag).localname
            except:
                raise SitemapError(f"Root tag does not have a name")
            return _element
        except Exception as e:
            self._logger.error(f"Invalid XML syntax: {str(e)}")
            raise SitemapError(f"Invalid XML syntax: {str(e)}")

    @property
    def entries(self) -> List:
        return self._entries

    @property
    def type(self) -> SitemapType:
        return self._type


class IndexNode(SitemapNode):
    def __init__(self, context: Context, document: str = None) -> None:
        super().__init__(context, document)
        if document is not None:
            _localname = etree.QName(self._root.tag).localname
            if _localname != SitemapType.INDEX.value:
                raise ValueError(
                    f"Expected a root {SitemapType.INDEX.value} got {_localname}"
                )
            self._entries = self._parse_index_sitemap(document)
        self._type = SitemapType.INDEX

    def _parse_index_sitemap(self, document) -> List[IndexEntry]:
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
            except ValueError as e:
                self._logger.warning(f"Error parsing sitemap reference: {e}")
        return sitemaps

    @property
    def entries(self) -> List[IndexEntry]:
        """Get the sitemaps in this index."""
        return self._entries

    @entries.setter
    def entries(self, entries: List[IndexEntry]) -> None:
        """
        Set the sitemaps in this index.

        Args:
            sitemaps: List of sitemap URLs
        """
        if not isinstance(entries, list):
            raise TypeError(f"Expected a list, got {type(entries)}")

        # Validate all items are of correct type
        for entry in entries:
            if not isinstance(entry, IndexEntry):
                raise TypeError(f"Expected IndexEntry, got {type(entry)}")

        self._entries = entries


class UrlsetNode(SitemapNode):
    def __init__(self, context: Context, document: str = None) -> None:
        super().__init__(context, document)
        if document is not None:
            _localname = etree.QName(self._root.tag).localname
            if _localname != SitemapType.URLSET.value:
                raise ValueError(
                    f"Expected a root {SitemapType.URLSET.value} got {_localname}"
                )
            self._entries = self._parse_urlset_sitemap(document)
        self._type = SitemapType.URLSET

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
            except ValueError as e:
                self._logger.warning(f"Error parsing sitemap reference: {e}")
        return urlset
