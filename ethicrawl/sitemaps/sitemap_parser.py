
from ethicrawl.config import Config
from ethicrawl.context import Context
from ethicrawl.core import Resource, ResourceList
from ethicrawl.error import SitemapError

from .const import SITEMAPINDEX, URLSET
from .index_entry import IndexEntry
from .index_node import IndexNode
from .sitemap_node import SitemapNode
from .urlset_node import UrlsetNode


class SitemapParser:
    def __init__(self, context: Context):
        self._context = context
        self._logger = self._context.logger("sitemap")

    def parse(
        self,
        root: IndexNode | ResourceList | list[Resource] | None = None,
    ) -> ResourceList:
        if isinstance(root, IndexNode):
            document = root
        else:
            # Handle different input types properly
            if isinstance(root, ResourceList):
                # Already a ResourceList, use directly
                resources = root
            else:
                # Convert other list-like objects or None
                resources = ResourceList(root or [])

            document = IndexNode(self._context)
            for resource in resources:
                document.entries.append(IndexEntry(resource.url))

        return self._traverse(document, 0)

    def _get(self, resource: Resource) -> SitemapNode:
        document = self._context.client.get(resource).text
        node = SitemapNode(self._context, document)
        if node.type == URLSET:
            return UrlsetNode(self._context, document)
        elif node.type == SITEMAPINDEX:
            return IndexNode(self._context, document)
        else:
            self._logger.warning(
                f"Unknown sitemap type with root element: {node.type}")
            raise SitemapError(
                f"Unknown sitemap type with root element: {node.type}")

    def _traverse(self, node: IndexNode, depth: int = 0, visited=None) -> ResourceList:
        # Collection of all found URLs
        max_depth = Config().sitemap.max_depth
        all_urls = ResourceList([])

        # Initialize visited set if this is the first call
        if visited is None:
            visited = set()

        # Check if we've reached maximum depth
        if depth >= max_depth:
            self._logger.warning(
                f"Maximum recursion depth ({max_depth}) reached, stopping traversal"
            )
            # Return empty ResourceList instead of None
            return ResourceList()

        self._logger.debug(
            f"Traversing IndexNode at depth {depth}, has {len(node.entries)} items"
        )

        for item in node.entries:
            # Process each entry and collect any URLs found
            urls = self._process_entry(item, depth, visited)
            all_urls.extend(urls)

        return all_urls

    def _process_entry(
        self, item: IndexEntry, depth: int, visited: set
    ) -> ResourceList:
        """Process a single sitemap entry, handling cycles and recursion."""
        url_str = str(item.url)

        # Check for cycles - skip if we've seen this URL before
        if url_str in visited:
            self._logger.warning(
                f"Cycle detected: {url_str} has already been processed"
            )
            return ResourceList()

        self._logger.debug(f"Processing item: {item.url}")
        document = self._get(Resource(item.url))

        # Mark this URL as visited
        visited.add(url_str)

        if document.type == SITEMAPINDEX:
            self._logger.debug(
                f"Found index sitemap with {len(document.entries)} items"
            )
            return self._traverse(document, depth + 1, visited)
        elif document.type == URLSET:
            self._logger.debug(
                f"Found urlset with {len(document.entries)} URLs")
            return document.entries

        # Empty list for any unhandled cases
        return ResourceList()  # pragma: no cover
