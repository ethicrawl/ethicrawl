from lxml import etree

from ethicrawl.context import Context
from ethicrawl.core import Url, ResourceList

from .const import SITEMAPINDEX
from .index_entry import IndexEntry
from .sitemap_document import SitemapDocument


class IndexDocument(SitemapDocument):
    """Specialized parser for sitemap index documents.

    This class extends the SitemapDocument class to handle sitemap indexes,
    which are XML documents containing references to other sitemap files.
    It validates that the document is a proper sitemap index and extracts
    all sitemap references as IndexEntry objects.

    IndexDocument enforces type safety for its entries collection, ensuring
    that only IndexEntry objects can be added.

    Attributes:
        entries: ResourceList of IndexEntry objects representing sitemap references

    Example:
        >>> from ethicrawl.context import Context
        >>> from ethicrawl.core import Resource
        >>> from ethicrawl.sitemaps import IndexDocument
        >>> context = Context(Resource("https://example.com"))
        >>> sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        ... <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        ...   <sitemap>
        ...     <loc>https://example.com/sitemap1.xml</loc>
        ...     <lastmod>2023-06-15T14:30:00Z</lastmod>
        ...   </sitemap>
        ... </sitemapindex>'''
        >>> index = IndexDocument(context, sitemap_xml)
        >>> len(index.entries)
        1
        >>> str(index.entries[0])
        'https://example.com/sitemap1.xml (last modified: 2023-06-15T14:30:00Z)'
    """

    def __init__(self, context: Context, document: str | None = None) -> None:
        """Initialize a sitemap index document parser.

        Args:
            context: Context for logging and resource resolution
            document: Optional XML sitemap index content to parse

        Raises:
            ValueError: If the document is not a valid sitemap index
            SitemapError: If the document cannot be parsed
        """
        super().__init__(context, document)
        self._logger.debug("Creating IndexDocument instance")

        if document is not None:
            _localname = etree.QName(self._root.tag).localname
            if _localname != SITEMAPINDEX:
                raise ValueError(f"Expected a root {SITEMAPINDEX} got {_localname}")
            self._entries = self._parse_index_sitemap(document)
            self._logger.debug(
                "Parsed sitemap index with %d entries", len(self._entries)
            )

    def _parse_index_sitemap(self, document) -> ResourceList:
        """Parse sitemap references from a sitemap index.

        Extracts all <sitemap> elements and their <loc> and <lastmod>
        children, creating IndexEntry objects for each valid reference.

        Args:
            document: XML document string to parse

        Returns:
            ResourceList containing IndexEntry objects for each sitemap reference
        """
        sitemaps: ResourceList = ResourceList()

        nsmap = {"": self.SITEMAP_NS}
        _root = etree.fromstring(document.encode("utf-8"), parser=self._parser)

        # Find all sitemap elements
        sitemap_elements = _root.findall(".//sitemap", namespaces=nsmap)
        self._logger.debug(
            "Found %d sitemap references in index", len(sitemap_elements)
        )

        for sitemap_elem in sitemap_elements:
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
            except ValueError as exc:  # pragma: no cover
                self._logger.warning("Error parsing sitemap reference: %s", exc)
        return sitemaps

    @property
    def entries(self) -> ResourceList:
        """Get the sitemaps in this index.

        Returns:
            ResourceList of IndexEntry objects representing sitemap references
        """
        return self._entries

    @entries.setter
    def entries(self, entries: ResourceList) -> None:
        """Set the sitemaps in this index.

        Args:
            entries: List of sitemap references as IndexEntry objects

        Raises:
            TypeError: If entries is not a ResourceList or contains non-IndexEntry objects
        """
        if not isinstance(entries, ResourceList):
            raise TypeError(f"Expected a ResourceList, got {type(entries).__name__}")

        # Validate all items are of correct type
        for entry in entries:
            if not isinstance(entry, IndexEntry):
                raise TypeError(f"Expected IndexEntry, got {type(entry).__name__}")

        self._logger.debug("Setting %d entries in sitemap index", len(entries))
        self._entries = entries
