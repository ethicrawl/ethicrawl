from typing import List, Union
from ethicrawl.core.context import Context
from ethicrawl.core.resource import Resource
from ethicrawl.sitemaps.sitemap_entries import IndexEntry
from ethicrawl.sitemaps.sitemap_nodes import IndexNode, UrlsetNode
from ethicrawl.sitemaps.sitemap_util import SitemapType
from ethicrawl.core.resource_list import ResourceList
from ethicrawl.config import Config


import lxml
from lxml import etree


class Sitemaps:
    def __init__(self, context: Context):
        self._context = context
        self._logger = self._context.logger("sitemap")

    def parse(self, root: Union[IndexNode, List[Resource]] = None) -> ResourceList:

        max_depth = Config().sitemap.max_depth

        if isinstance(root, IndexNode):
            document = root
        else:
            document = IndexNode(self._context)
            for resource in root:
                document.entries.append(IndexEntry(resource.url))

            # self._logger.debug(type(document), document.entries)

        def _get(resource: Resource):
            response = self._context.client.get(resource)

            # Instead of relying on SitemapNode to determine type, check directly
            document = response.text

            # Quick check of the XML root element name
            try:
                parser = etree.XMLParser(
                    resolve_entities=False,  # Prevent XXE attacks
                    no_network=True,  # Prevent external resource loading
                    dtd_validation=False,  # Don't validate DTDs
                    load_dtd=False,  # Don't load DTDs at all
                    huge_tree=False,  # Prevent XML bomb attacks
                )
                root = etree.fromstring(document.encode("utf-8"), parser)
                root_tag = etree.QName(root.tag).localname
                self._logger.debug(f"Root tag: {root_tag}")

                if root_tag == SitemapType.INDEX.value:
                    index_node = IndexNode(self._context, document)
                    self._logger.debug(
                        f"Created IndexNode with {len(index_node.entries)} items"
                    )
                    return index_node
                elif root_tag == SitemapType.URLSET.value:
                    urlset_node = UrlsetNode(self._context, document)
                    self._logger.debug(
                        f"Created UrlsetNode with {len(urlset_node.entries)} items"
                    )
                    return urlset_node
                else:
                    self._logger.warning(
                        f"Unknown sitemap type with root element: {root_tag}"
                    )
                    raise ValueError(
                        f"Unknown sitemap type with root element: {root_tag}"
                    )

            except Exception as e:
                self._logger.error(f"Failed to parse sitemap XML: {str(e)}")
                raise ValueError(f"Failed to parse sitemap XML: {str(e)}")

        def _traverse(
            node: IndexNode, depth: int = 0, max_depth: int = max_depth, visited=None
        ):
            # Collection of all found URLs
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
                url_str = str(item.url)

                # Check for cycles - skip if we've seen this URL before
                if url_str in visited:
                    self._logger.warning(
                        f"Cycle detected: {url_str} has already been processed"
                    )
                    continue

                # Mark this URL as visited
                visited.add(url_str)
                self._logger.debug(f"Processing item: {item.url}")
                document = _get(Resource(item.url))
                if document.type == SitemapType.INDEX:
                    self._logger.debug(
                        f"Found index sitemap with {len(document.entries)} items"
                    )
                    nested_urls = _traverse(document, depth + 1, max_depth, visited)
                    all_urls.extend(nested_urls)
                elif document.type == SitemapType.URLSET:
                    self._logger.debug(
                        f"Found urlset with {len(document.entries)} URLs"
                    )
                    all_urls.extend(document.entries)
            return all_urls

        result = _traverse(document, 0)

        return result
