from lxml import etree

from ethicrawl.context import Context
from ethicrawl.core import Url, ResourceList

from .const import URLSET
from .sitemap_document import SitemapDocument
from .urlset_entry import UrlsetEntry


class UrlsetDocument(SitemapDocument):
    """Specialized parser for sitemap urlset documents.

    This class extends SitemapDocument to handle urlset sitemaps,
    which contain page URLs with metadata like change frequency and priority.
    It validates that the document is a proper urlset and extracts all
    URL references as UrlsetEntry objects.

    UrlsetDocument supports only the core sitemap protocol specification
    elements (loc, lastmod, changefreq, priority) and does not handle any
    sitemap protocol extensions.

    Attributes:
        entries: ResourceList of UrlsetEntry objects representing page URLs

    Example:
        >>> from ethicrawl.context import Context
        >>> from ethicrawl.core import Resource
        >>> from ethicrawl.sitemaps import UrlsetDocument
        >>> context = Context(Resource("https://example.com"))
        >>> sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        ... <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        ...   <url>
        ...     <loc>https://example.com/page1</loc>
        ...     <lastmod>2023-06-15T14:30:00Z</lastmod>
        ...     <changefreq>weekly</changefreq>
        ...     <priority>0.8</priority>
        ...   </url>
        ... </urlset>'''
        >>> urlset = UrlsetDocument(context, sitemap_xml)
        >>> len(urlset.entries)
        1
        >>> entry = urlset.entries[0]
        >>> entry.priority
        '0.8'
    """

    def __init__(self, context: Context, document: str | None = None) -> None:
        """Initialize a urlset sitemap document parser.

        Args:
            context: Context for logging and resource resolution
            document: Optional XML urlset content to parse

        Raises:
            ValueError: If the document is not a valid urlset
            SitemapError: If the document cannot be parsed
        """
        super().__init__(context, document)
        self._logger.debug("Creating UrlsetDocument instance")

        if document is not None:
            _localname = etree.QName(self._root.tag).localname
            if _localname != URLSET:
                raise ValueError(f"Expected a root {URLSET} got {_localname}")
            self._entries = self._parse_urlset_sitemap(document)
            self._logger.debug("Parsed urlset with %d entries", len(self._entries))

    def _parse_urlset_sitemap(self, document) -> ResourceList:
        """Parse page URLs from a urlset sitemap.

        Extracts all <url> elements and their children (<loc>, <lastmod>,
        <changefreq>, <priority>), creating UrlsetEntry objects for each
        valid URL entry.

        Args:
            document: XML document string to parse

        Returns:
            ResourceList containing UrlsetEntry objects for each URL
        """
        urlset: ResourceList = ResourceList()

        nsmap = {"": self.SITEMAP_NS}
        _root = etree.fromstring(document.encode("utf-8"), parser=self._parser)

        # Find all url elements
        url_elements = _root.findall(".//url", namespaces=nsmap)
        self._logger.debug("Found %d URL entries in urlset", len(url_elements))

        for url_elem in url_elements:
            try:
                loc_elem = url_elem.find("loc", namespaces=nsmap)
                if loc_elem is None or not loc_elem.text:
                    continue

                # Get optional elements
                lastmod_elem = url_elem.find("lastmod", namespaces=nsmap)
                changefreq_elem = url_elem.find("changefreq", namespaces=nsmap)
                priority_elem = url_elem.find("priority", namespaces=nsmap)

                url = UrlsetEntry(
                    url=Url(loc_elem.text),
                    lastmod=lastmod_elem.text if lastmod_elem is not None else None,
                    changefreq=(
                        changefreq_elem.text if changefreq_elem is not None else None
                    ),
                    priority=(
                        priority_elem.text if priority_elem is not None else None
                    ),
                )

                urlset.append(url)
            except ValueError as e:  # pragma: no cover
                self._logger.warning("Error parsing sitemap reference: %s", e)
        return urlset

    @property
    def entries(self) -> ResourceList:
        """Get the URLs in this urlset.

        Returns:
            ResourceList of UrlsetEntry objects representing page URLs
        """
        return self._entries

    @entries.setter
    def entries(self, entries: ResourceList) -> None:
        """Set the URLs in this urlset.

        Args:
            entries: List of page URLs as UrlsetEntry objects

        Raises:
            TypeError: If entries is not a ResourceList or contains non-UrlsetEntry objects
        """
        if not isinstance(entries, ResourceList):
            raise TypeError("entries must be a ResourceList")
        for entry in entries:
            if not isinstance(entry, UrlsetEntry):
                raise TypeError("entries must contain only UrlsetEntry objects")
        self._entries = entries
