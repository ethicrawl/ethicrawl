from abc import ABC, abstractmethod
from typing import List, Optional
from lxml import etree

from lxml import html
from typing import List, Optional, Set
import lxml
import gzip
from ethicrawl.client import HttpClient


import lxml

from ethicrawl.logger import LoggingMixin
from .sitemap_urls import SitemapIndexUrl, SitemapUrlsetUrl
from .sitemap_util import SitemapError, SitemapHelper, SitemapType
from ethicrawl.core import EthicrawlContext
from ethicrawl.logger import LoggingMixin
from ethicrawl.config import Config


class SitemapNode(ABC, LoggingMixin):
    """Should never be instantiated directly"""

    SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

    @staticmethod
    def get_lxml(context: EthicrawlContext, document: str) -> lxml.etree._Element:
        # preparse
        logger = context.get_logger("sitemap.node")
        document = SitemapHelper.escape_unescaped_ampersands(document)
        try:
            _element = etree.fromstring(document.encode("utf-8"))
        except Exception as e:
            logger.error(f"Invalid XML syntax: {str(e)}")
            raise SitemapError(f"Invalid XML syntax: {str(e)}")
        if _element.nsmap[None] != SitemapNode.SITEMAP_NS:
            logger.error(
                f"Required default namespace not found: {SitemapNode.SITEMAP_NS}"
            )
            raise SitemapError(
                f"Required default namespace not found: {SitemapNode.SITEMAP_NS}"
            )
        try:
            _ = lxml.etree.QName(_element.tag).localname
        except:
            raise SitemapError(f"Root tag does not have a name")
        return _element

    def __init__(
        self, context: EthicrawlContext, document: Optional[str] = None
    ) -> None:
        self._context = context
        self._setup_logger(self._context.url, "sitemap.node")
        self._source_url = None

        if document is not None:
            # Parse document if provided
            self._root = self.get_lxml(context, document)
            document_type = lxml.etree.QName(self._root.tag).localname
            if document_type == "urlset":
                self._type = SitemapType.URLSET
            elif document_type == "sitemapindex":
                self._type = SitemapType.INDEX
            else:
                self._type = SitemapType.UNDEFINED
        else:
            # No document - subclasses will set their type
            self._root = None

    @property
    def source_url(self) -> Optional[SitemapIndexUrl]:
        return self._source_url

    @source_url.setter
    def source_url(self, url: SitemapIndexUrl) -> None:
        if isinstance(url, SitemapIndexUrl):
            self._source_url = url
        else:
            self._logger.warning(f"Expected a SitemapIndexUrl, got {type(url)}")
            raise ValueError(f"Expected a SitemapIndexUrl, got {type(url)}")

    @property
    def type(self) -> SitemapType:
        """Get the type of this sitemap node."""
        return self._type

    @property
    @abstractmethod
    def items(self):
        """
        Get the items in this sitemap.

        Returns:
            List: Either List[SitemapUrlsetUrl] (for urlset) or List[SitemapIndexUrl] (for index)
        """
        pass

    @items.setter
    @abstractmethod
    def items(self, value):
        """Set the items in this sitemap."""
        pass


# class IndexNode(SitemapNode, LoggingMixin):
#     """Node representing a sitemap index."""

#     def __init__(self, context: EthicrawlContext, document: str) -> None:
#         super().__init__(context, document)
#         self._logger = context.get_logger("sitemap.node.index")
#         self._sitemaps = None
#         local_name = lxml.etree.QName(self._root.tag).localname

#         if self._type != SitemapType.INDEX:
#             self._logger.warning(
#                 f"Not a sitemap index document. Root element is '{local_name}', expected 'sitemapindex'"
#             )
#             raise SitemapError(
#                 f"Not a sitemap index document. Root element is '{local_name}', expected 'sitemapindex'"
#             )


class IndexNode(SitemapNode):
    """Node representing a sitemap index."""

    def __init__(
        self, context: EthicrawlContext, document: Optional[str] = None
    ) -> None:
        # Initialize base with or without document
        super().__init__(context, document)
        self._logger = context.get_logger("sitemap.node.index")
        self._sitemaps = []  # Start with empty list

        if document is None:
            # For empty node, just set the type directly
            self._type = SitemapType.INDEX
        else:
            # Validate parsed document type
            if self._type != SitemapType.INDEX:
                local_name = lxml.etree.QName(self._root.tag).localname
                self._logger.warning(
                    f"Not a sitemap index document. Root element is '{local_name}', expected 'sitemapindex'"
                )
                raise SitemapError(
                    f"Not a sitemap index document. Root element is '{local_name}', expected 'sitemapindex'"
                )

    @property
    def items(self) -> List[SitemapIndexUrl]:
        """Get the sitemaps in this index."""
        if self._sitemaps is None:
            self._sitemaps = self._parse_sitemaps()
        return self._sitemaps

    @items.setter
    def items(self, sitemaps: List[SitemapIndexUrl]) -> None:
        """
        Set the sitemaps in this index.

        Args:
            sitemaps: List of sitemap URLs
        """
        if not isinstance(sitemaps, list):
            raise TypeError(f"Expected a list, got {type(sitemaps)}")

        # Validate all items are of correct type
        for item in sitemaps:
            if not isinstance(item, SitemapIndexUrl):
                raise TypeError(f"Expected SitemapIndexUrl, got {type(item)}")

        self._sitemaps = sitemaps

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
                self._logger.warning(f"Error parsing sitemap reference: {e}")
        return sitemaps


class UrlsetNode(SitemapNode, LoggingMixin):
    """Node representing a sitemap urlset."""

    def __init__(self, context: EthicrawlContext, document: str) -> None:
        super().__init__(context, document)
        self._logger = context.get_logger("sitemap.node.urlset")
        self._urls = None
        local_name = lxml.etree.QName(self._root.tag).localname

        if self._type != SitemapType.URLSET:
            self._logger.warning(
                f"Not a urlset document. Root element is '{local_name}', expected 'urlset'"
            )
            raise SitemapError(
                f"Not a urlset document. Root element is '{local_name}', expected 'urlset'"
            )

    # In UrlsetNode class (implement the setter)
    @property
    def items(self) -> List[SitemapUrlsetUrl]:
        """Get the URLs in this urlset."""
        if self._urls is None:
            self._urls = self._parse_urls()
        return self._urls

    @items.setter
    def items(self, urls: List[SitemapUrlsetUrl]) -> None:
        """
        Set the URLs in this urlset.

        Args:
            urls: List of sitemap URLs
        """
        if not isinstance(urls, list):
            raise TypeError(f"Expected a list, got {type(urls)}")

        # Validate all items are of correct type
        for item in urls:
            if not isinstance(item, SitemapUrlsetUrl):
                raise TypeError(f"Expected SitemapUrlsetUrl, got {type(item)}")

        self._urls = urls

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
                self._logger.warning(f"Error parsing URL: {e}")

        return urls
