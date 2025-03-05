from abc import ABC, abstractmethod
from typing import List, Optional
from lxml import etree


import lxml

from ethicrawl.logger import LoggingMixin
from .sitemap_urls import SitemapIndexUrl, SitemapUrlsetUrl
from .sitemap_util import SitemapError, SitemapHelper, SitemapType


class SitemapNode(ABC):
    """Should never be instantiated directly"""

    SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

    @staticmethod
    def get_lxml(document: str) -> lxml.etree._Element:
        # preparse
        document = SitemapHelper.escape_unescaped_ampersands(document)
        try:
            _element = etree.fromstring(document.encode("utf-8"))
        except Exception as e:
            raise SitemapError(f"Invalid XML syntax: {str(e)}")
        if _element.nsmap[None] != SitemapNode.SITEMAP_NS:
            raise SitemapError(
                f"Required default namespace not found: {SitemapNode.SITEMAP_NS}"
            )
        try:
            _ = lxml.etree.QName(_element.tag).localname
        except:
            raise SitemapError(f"Root tag does not have a name")
        return _element

    def __init__(self, document: str) -> None:
        self._root = self.get_lxml(document=document)
        document_type = lxml.etree.QName(self._root.tag).localname
        if document_type == "urlset":
            self._type = SitemapType.URLSET
        elif document_type == "sitemapindex":
            self._type = SitemapType.INDEX
        else:
            self._type = SitemapType.UNDEFINED
        self._source_url = None

    @property
    def source_url(self) -> Optional[SitemapIndexUrl]:  # could also return None
        return self._source_url

    @source_url.setter
    def source_url(self, url: SitemapIndexUrl) -> None:
        if isinstance(url, SitemapIndexUrl):
            self._source_url = url
        else:
            raise ValueError(f"Expected a SitemapIndexUrl, got {type(url)}")

    @property
    def type(self) -> SitemapType:
        """Get the type of this sitemap node."""
        return self._type

    @property
    @abstractmethod
    def items(self) -> List:
        """
        Get the items in this sitemap.

        Returns:
            List: Either List[SitemapUrlsetUrl] (for urlset) or List[SitemapIndexUrl] (for index)
        """
        pass


class IndexNode(SitemapNode, LoggingMixin):
    """Node representing a sitemap index."""

    def __init__(self, document: str) -> None:
        super().__init__(document)
        self._sitemaps = None
        local_name = lxml.etree.QName(self._root.tag).localname

        if self._type != SitemapType.INDEX:
            raise SitemapError(
                f"Not a sitemap index document. Root element is '{local_name}', expected 'sitemapindex'"
            )

    @property
    def items(self) -> List[SitemapIndexUrl]:
        if self._sitemaps is None:
            self._sitemaps = self._parse_sitemaps()
        return self._sitemaps

    def _parse_sitemaps(self) -> List[SitemapIndexUrl]:
        """Parse sitemap references from a sitemap index."""
        sitemaps = []
        nsmap = {None: self.SITEMAP_NS}

        # Find all sitemap elements
        for sitemap_elem in self._root.findall(".//sitemap", namespaces=nsmap):
            try:
                # Get the required loc element
                loc_elem = sitemap_elem.find("loc", namespaces=nsmap)
                if loc_elem is None or not loc_elem.text:
                    continue

                # Get optional lastmod element
                lastmod_elem = sitemap_elem.find("lastmod", namespaces=nsmap)

                # Create SitemapIndexUrl object (only loc and lastmod)
                sitemap_url = SitemapIndexUrl(
                    loc=loc_elem.text,
                    lastmod=lastmod_elem.text if lastmod_elem is not None else None,
                )

                sitemaps.append(sitemap_url)
            except ValueError as e:
                print(f"Error parsing sitemap reference: {e}")

        return sitemaps


class UrlsetNode(SitemapNode, LoggingMixin):
    """Node representing a sitemap urlset."""

    def __init__(self, document: str) -> None:
        super().__init__(document)
        self._urls = None
        local_name = lxml.etree.QName(self._root.tag).localname

        if self._type != SitemapType.URLSET:
            raise SitemapError(
                f"Not a urlset document. Root element is '{local_name}', expected 'urlset'"
            )

    @property
    def items(self) -> List[SitemapUrlsetUrl]:
        if self._urls is None:
            pass
            self._urls = self._parse_urls()
        return self._urls

    def _parse_urls(self) -> List[SitemapUrlsetUrl]:
        """Parse URLs from a sitemap urlset."""
        urls = []
        nsmap = {None: self.SITEMAP_NS}  # namespace mapping for the default namespace

        # Find all url elements
        for url_elem in self._root.findall(".//url", namespaces=nsmap):
            try:
                # Get the required loc element
                loc_elem = url_elem.find("loc", namespaces=nsmap)
                if loc_elem is None or not loc_elem.text:
                    continue

                # Get optional elements
                lastmod_elem = url_elem.find("lastmod", namespaces=nsmap)
                changefreq_elem = url_elem.find("changefreq", namespaces=nsmap)
                priority_elem = url_elem.find("priority", namespaces=nsmap)

                # Create SitemapUrlsetUrl object - validation happens in __post_init__
                url = SitemapUrlsetUrl(
                    loc=loc_elem.text,
                    lastmod=lastmod_elem.text if lastmod_elem is not None else None,
                    changefreq=(
                        changefreq_elem.text if changefreq_elem is not None else None
                    ),
                    priority=priority_elem.text if priority_elem is not None else None,
                )

                urls.append(url)
            except ValueError as e:
                print(f"Error parsing URL: {e}")

        return urls
