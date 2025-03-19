from re import sub
from typing import List

from lxml import etree

from ethicrawl.context import Context

from .const import SITEMAPINDEX, URLSET
from .sitemap_error import SitemapError


class SitemapNode:
    SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

    def __init__(self, context: Context, document: str = None) -> None:
        self._context = context
        self._logger = self._context.logger("sitemap.node")
        self._entries = []
        self._parser = etree.XMLParser(
            resolve_entities=False,  # Prevent XXE attacks
            no_network=True,  # Prevent external resource loading
            dtd_validation=False,  # Don't validate DTDs
            load_dtd=False,  # Don't load DTDs at all
            huge_tree=False,  # Prevent XML bomb attacks
        )
        if document is not None:
            self._root = self._validate(document)

    def _escape_unescaped_ampersands(self, xml_document: str) -> str:
        """Escape unescaped ampersands in XML content."""
        pattern = r"&(?!(?:[a-zA-Z]+|#[0-9]+|#x[0-9a-fA-F]+);)"
        return sub(pattern, "&amp;", xml_document)

    def _validate(self, document: str) -> etree._Element:
        document = self._escape_unescaped_ampersands(
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
            return _element
        except Exception as e:
            self._logger.error(f"Invalid XML syntax: {str(e)}")
            raise SitemapError(f"Invalid XML syntax: {str(e)}")

    @property
    def entries(self) -> List:
        return self._entries

    @property
    def type(self) -> str:
        """Return the local name of the root element (e.g., 'urlset', 'sitemapindex')."""
        if not hasattr(self, "_root"):  # pragma: no cover
            raise SitemapError(
                "No root name"
            )  # I dont think this would ever happen due to validation rules
        if etree.QName(self._root.tag).localname in [SITEMAPINDEX, URLSET]:
            return etree.QName(self._root.tag).localname
        else:
            return "unsupported"
