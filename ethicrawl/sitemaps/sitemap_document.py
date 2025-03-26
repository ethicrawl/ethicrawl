from re import sub

from lxml import etree

from ethicrawl.context import Context
from ethicrawl.core import ResourceList
from ethicrawl.error import SitemapError

from .const import SITEMAPINDEX, URLSET


class SitemapDocument:
    """Parser and representation of XML sitemap documents.

    This class handles the parsing, validation, and extraction of entries from
    XML sitemap documents, supporting both sitemap index files and urlset files.
    It implements security best practices for XML parsing to prevent common
    vulnerabilities like XXE attacks.

    SitemapDocument distinguishes between sitemap indexes (which contain references
    to other sitemaps) and urlsets (which contain actual page URLs), extracting
    the appropriate entries in each case.

    Attributes:
        SITEMAP_NS: The official sitemap namespace URI
        entries: ResourceList containing the parsed sitemap entries
        type: The type of sitemap (sitemapindex, urlset, or unsupported)

    Example:
        >>> from ethicrawl.context import Context
        >>> from ethicrawl.core import Resource
        >>> from ethicrawl.sitemaps import SitemapDocument
        >>> context = Context(Resource("https://example.com"))
        >>> sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        ... <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        ...   <url>
        ...     <loc>https://example.com/page1</loc>
        ...     <lastmod>2023-06-15T14:30:00Z</lastmod>
        ...   </url>
        ... </urlset>'''
        >>> sitemap = SitemapDocument(context, sitemap_xml)
        >>> sitemap.type
        'urlset'
        >>> len(sitemap.entries)
        1
    """

    SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

    def __init__(self, context: Context, document: str | None = None) -> None:
        """Initialize a sitemap document parser with security protections.

        Sets up the XML parser with security features to prevent common
        XML vulnerabilities and optionally parses a provided document.

        Args:
            context: Context for logging and resource resolution
            document: Optional XML sitemap content to parse immediately

        Raises:
            SitemapError: If the provided document cannot be parsed
        """
        self._context = context
        self._logger = self._context.logger("sitemap.document")
        # Add debug logging
        self._logger.debug("Creating new SitemapDocument instance")
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
        """Escape unescaped ampersands in XML content.

        Args:
            xml_document: Raw XML string that may contain unescaped ampersands

        Returns:
            XML string with properly escaped ampersands
        """
        pattern = r"&(?!(?:[a-zA-Z]+|#[0-9]+|#x[0-9a-fA-F]+);)"
        return sub(pattern, "&amp;", xml_document)

    def _validate(self, document: str) -> etree._Element:
        """Validate and parse a sitemap XML document.

        This method:
        1. Escapes unescaped ampersands in the document
        2. Parses the XML using the secure parser
        3. Validates that it uses the correct sitemap namespace

        Args:
            document: XML document string to parse

        Returns:
            The parsed XML element tree root

        Raises:
            SitemapError: If the document has invalid XML or incorrect namespace
        """
        document = self._escape_unescaped_ampersands(
            document
        )  # TODO: might want to move this to the HttpClient
        try:
            _element = etree.fromstring(document.encode("utf-8"), parser=self._parser)
            if _element.nsmap[None] != SitemapDocument.SITEMAP_NS:
                self._logger.error(
                    "Required default namespace not found: %s",
                    SitemapDocument.SITEMAP_NS,
                )
                raise SitemapError(
                    f"Required default namespace not found: {SitemapDocument.SITEMAP_NS}"
                )
            return _element
        except Exception as e:
            self._logger.error("Invalid XML syntax: %s", e)
            raise SitemapError(f"Invalid XML syntax: {str(e)}") from e

    @property
    def entries(self) -> ResourceList:
        """Get the list of entries extracted from the sitemap.

        Returns:
            ResourceList containing SitemapEntry objects (either IndexEntry
            or UrlsetEntry depending on the sitemap type)
        """
        return self._entries

    @property
    def type(self) -> str:
        """Get the type of sitemap document.

        Determines the type based on the root element's local name.

        Returns:
            String indicating the sitemap type:
            - 'sitemapindex': A sitemap index containing references to other sitemaps
            - 'urlset': A sitemap containing page URLs
            - 'unsupported': Any other type of document

        Raises:
            SitemapError: If no document has been loaded
        """
        if not hasattr(self, "_root"):  # pragma: no cover
            raise SitemapError("No root name")

        localname = etree.QName(self._root.tag).localname
        if localname in [SITEMAPINDEX, URLSET]:
            self._logger.debug("Identified sitemap type: %s", localname)
            return localname

        self._logger.warning("Unsupported sitemap document type: %s", localname)
        return "unsupported"
