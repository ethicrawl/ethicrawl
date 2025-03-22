from re import sub

from lxml import etree

from ethicrawl.context import Context
from ethicrawl.core import ResourceList
from ethicrawl.error import SitemapError

from .const import SITEMAPINDEX, URLSET


class SitemapNode:
    SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

    def __init__(self, context: Context, document: str | None = None) -> None:
        self._context = context
        self._logger = self._context.logger("sitemap.node")
        # Add debug logging
        self._logger.debug("Creating new SitemapNode instance")
        self._entries: ResourceList = ResourceList()
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
                    "Required default namespace not found: %s", SitemapNode.SITEMAP_NS
                )
                raise SitemapError(
                    f"Required default namespace not found: {SitemapNode.SITEMAP_NS}"
                )
            return _element
        except Exception as e:
            self._logger.error("Invalid XML syntax: %s", e)
            raise SitemapError(f"Invalid XML syntax: {str(e)}") from e

    @property
    def entries(self) -> ResourceList:
        return self._entries

    @property
    def type(self) -> str:
        """Return the local name of the root element."""
        if not hasattr(self, "_root"):  # pragma: no cover
            raise SitemapError("No root name")

        localname = etree.QName(self._root.tag).localname
        if localname in [SITEMAPINDEX, URLSET]:
            self._logger.debug("Identified sitemap type: %s", localname)
            return localname

        self._logger.warning("Unsupported sitemap node type: %s", localname)
        return "unsupported"
