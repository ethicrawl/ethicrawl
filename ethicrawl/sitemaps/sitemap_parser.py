from ethicrawl.config import Config
from ethicrawl.context import Context
from ethicrawl.core import Resource, ResourceList
from ethicrawl.error import SitemapError
from ethicrawl.client import Client

from .const import SITEMAPINDEX, URLSET
from .index_entry import IndexEntry
from .index_document import IndexDocument
from .sitemap_document import SitemapDocument
from .urlset_document import UrlsetDocument


class SitemapParser:
    """Recursive parser for extracting URLs from sitemap documents.

    This class handles the traversal of sitemap structures, including nested
    sitemap indexes, to extract all page URLs. It implements:

    - Recursive traversal of sitemap indexes
    - Depth limiting to prevent excessive recursion
    - Cycle detection to prevent infinite loops
    - URL deduplication
    - Multiple input formats (IndexDocument, ResourceList, etc.)

    Attributes:
        context: Context with client for fetching sitemaps and logging

    Example:
        >>> from ethicrawl.context import Context
        >>> from ethicrawl.core import Resource, Url
        >>> from ethicrawl.sitemaps import SitemapParser
        >>> context = Context(Resource(Url("https://example.com")))
        >>> parser = SitemapParser(context)
        >>> # Parse from a single sitemap URL
        >>> urls = parser.parse([Resource(Url("https://example.com/sitemap.xml"))])
        >>> print(f"Found {len(urls)} URLs in sitemap")
    """

    def __init__(self, context: Context):
        """Initialize the sitemap parser.

        Args:
            context: Context with client for fetching sitemaps and logging
        """
        self._context = context
        self._logger = self._context.logger("sitemap")

    def parse(
        self,
        root: IndexDocument | ResourceList | list[Resource] | None = None,
    ) -> ResourceList:
        """Parse sitemap(s) and extract all contained URLs.

        This is the main entry point for sitemap parsing. It accepts various
        input formats and recursively extracts all URLs from the sitemap(s).

        Args:
            root: Source to parse, which can be:
                - IndexDocument: Pre-parsed sitemap index
                - ResourceList: List of resources to fetch as sitemaps
                - list[Resource]: List of resources to fetch as sitemaps
                - None: Use the context's base URL for robots.txt discovery

        Returns:
            ResourceList containing all page URLs found in the sitemap(s)

        Raises:
            SitemapError: If a sitemap cannot be fetched or parsed
        """
        self._logger.debug("Starting sitemap parsing")

        if isinstance(root, IndexDocument):
            self._logger.debug("Parsing from provided IndexDocument")
            document = root
        else:
            # Handle different input types properly
            if isinstance(root, ResourceList):
                # Already a ResourceList, use directly
                resources = root
            else:
                # Convert other list-like objects or None
                resources = ResourceList(root or [])

            document = IndexDocument(self._context)
            for resource in resources:
                document.entries.append(IndexEntry(resource.url))

        return self._traverse(document, 0)

    def _get(self, resource: Resource) -> IndexDocument | SitemapDocument:
        """Fetch and parse a sitemap document from a resource.

        Retrieves the resource using the context's client and attempts
        to parse it as a sitemap document, determining the correct type
        (index or urlset).

        Args:
            resource: Resource to fetch and parse

        Returns:
            Parsed sitemap document (either IndexDocument or UrlsetDocument)

        Raises:
            SitemapError: If the document cannot be fetched or parsed
        """
        if not isinstance(self._context.client, Client):
            raise TypeError(
                f"Expected Client instance, got {type(self._context.client).__name__}"
            )
        self._logger.debug("Fetching sitemap from %s", resource.url)
        response = self._context.client.get(resource)

        # Handle different response types
        if hasattr(response, "text"):
            self._logger.debug("Using text attribute from response")
            content = response.text  # pyright: ignore[reportAttributeAccessIssue]
        elif hasattr(response, "content") and isinstance(response.content, str):
            self._logger.debug("Using string content attribute from response")
            content = response.content
        elif hasattr(response, "content"):
            # Content attribute that needs decoding
            content = response.content.decode("utf-8")
        else:
            # Fallback - convert response to string
            content = str(response)

        document = SitemapDocument(self._context, content)
        if document.type == URLSET:
            return UrlsetDocument(self._context, content)
        elif document.type == SITEMAPINDEX:
            return IndexDocument(self._context, content)
        self._logger.warning(
            "Unknown sitemap type with root element: %s", document.type
        )
        raise SitemapError(f"Unknown sitemap type with root element: {document.type}")

    def _traverse(
        self, document: IndexDocument | SitemapDocument, depth: int = 0, visited=None
    ) -> ResourceList:
        """Recursively traverse a sitemap document and extract URLs.

        Handles depth limiting and crawls nested sitemaps up to the
        configured maximum depth.

        Args:
            document: Sitemap document to traverse
            depth: Current recursion depth
            visited: Set of already processed sitemap URLs to prevent cycles

        Returns:
            ResourceList containing all URLs found in the traverse
        """
        # Collection of all found URLs
        if not isinstance(document, IndexDocument):  # pragma: no cover
            # we shouldn't be here
            return ResourceList()
        max_depth = Config().sitemap.max_depth
        all_urls: ResourceList = ResourceList([])

        # Initialize visited set if this is the first call
        if visited is None:
            visited = set()

        # Check if we've reached maximum depth
        if depth >= max_depth:
            self._logger.warning(
                "Maximum recursion depth (%d) reached, stopping traversal", max_depth
            )
            # Return empty ResourceList instead of None
            return ResourceList()

        self._logger.debug(
            "Traversing IndexDocument at depth %d, has %d items",
            depth,
            len(document.entries),
        )

        for item in document.entries:
            # Process each entry and collect any URLs found
            urls = self._process_entry(item, depth, visited)
            all_urls.extend(urls)

        return all_urls

    def _process_entry(
        self, item: IndexEntry, depth: int, visited: set
    ) -> ResourceList:
        """Process a single sitemap entry, handling cycles and recursion.

        Args:
            item: Sitemap entry to process
            depth: Current recursion depth
            visited: Set of already processed sitemap URLs

        Returns:
            ResourceList of URLs found in this entry (and any nested entries)
        """
        url_str = str(item.url)

        # Check for cycles - skip if we've seen this URL before
        if url_str in visited:
            self._logger.warning(
                "Cycle detected: %s has already been processed", url_str
            )
            return ResourceList()

        self._logger.debug("Processing item: %s", item.url)
        document = self._get(Resource(item.url))

        # Mark this URL as visited
        visited.add(url_str)

        if document.type == SITEMAPINDEX:
            self._logger.debug(
                "Found index sitemap with %d items", len(document.entries)
            )
            return self._traverse(document, depth + 1, visited)
        elif document.type == URLSET:
            self._logger.debug("Found urlset with %d URLs", len(document.entries))
            return document.entries

        # Empty list for any unhandled cases
        return ResourceList()  # pragma: no cover
