from typing import List, Optional
from ethicrawl.config.config import Config
from ethicrawl.client import HttpClient
from ethicrawl.logger import LoggingMixin
from ethicrawl.sitemaps.sitemap_urls import SitemapUrlsetUrl
from ethicrawl.sitemaps.node_factory import NodeFactory
from ethicrawl.sitemaps.sitemap_nodes import IndexNode, UrlsetNode

from ethicrawl.core import EthicrawlContext

import re


class Sitemap(LoggingMixin):
    """Builds sitemap trees and extracts URLs."""

    def __init__(self, context: EthicrawlContext, url_filter: Optional[str] = None):
        """
        Initialize the sitemap processor.

        Args:
            url_filter: Optional regex pattern to filter top-level sitemaps
        """
        self._context = context
        self.url_filter = re.compile(url_filter) if url_filter else None

    def items(self, root_node: IndexNode, max_depth: int = 5) -> List[SitemapUrlsetUrl]:
        """
        Build a sitemap tree and return a flat list of all URLs.

        Args:
            root_node: Root IndexNode to build from
            http_client: HTTP client for making requests
            max_depth: Maximum recursion depth for sitemap processing

        Returns:
            List of all SitemapUrlsetUrl objects from all sitemaps
        """
        # Initialize tracking set for cycle detection
        logger = self._context.get_logger("sitemap")
        visited_urls = set()

        if self.url_filter:
            original_count = len(root_node.items)
            root_node.items = [
                item for item in root_node.items if self.url_filter.search(item.loc)
            ]
            filtered_count = len(root_node.items)

            if filtered_count < original_count:
                logger.info(
                    f"Filtered sitemaps with pattern '{self.url_filter.pattern}': "
                    f"{filtered_count}/{original_count} remaining"
                )

        # Define the recursive implementation as an inner function
        def _build_tree_recursive(
            node: IndexNode, current_depth: int = 0
        ) -> List[SitemapUrlsetUrl]:
            all_urls = []

            # Check recursion depth
            if current_depth >= max_depth:
                logger.warning(
                    f"Warning: Maximum recursion depth ({max_depth}) reached. Some sitemaps may not be processed."
                )
                return all_urls

            # Create placeholder for children if needed
            if not hasattr(node, "children"):
                node.children = []

            # Process all sitemap URLs in the node
            for sitemap_url in node.items:
                try:
                    # Skip already visited URLs to prevent cycles
                    if sitemap_url.loc in visited_urls:
                        logger.debug(
                            f"Skipping already visited sitemap: {sitemap_url.loc}"
                        )
                        continue

                    logger.debug(f"Processing sitemap: {sitemap_url.loc}")

                    # Mark this URL as visited
                    visited_urls.add(sitemap_url.loc)

                    # Fetch and parse this child sitemap
                    child_node = NodeFactory.create(self._context, sitemap_url)

                    # If it's another index node, recursively build its tree
                    if isinstance(child_node, IndexNode):
                        # Recursively collect URLs
                        child_urls = _build_tree_recursive(
                            child_node, current_depth + 1
                        )
                        all_urls.extend(child_urls)

                    # If it's a urlset node, collect its URLs directly
                    elif isinstance(child_node, UrlsetNode) and hasattr(
                        child_node, "items"
                    ):
                        all_urls.extend(child_node.items)

                    # Add to parent's children list
                    node.children.append(child_node)

                except Exception as e:
                    logger.warning(
                        f"Error processing sitemap URL {sitemap_url.loc}: {str(e)}"
                    )
                    continue

            logger.info(
                f"Visited {len(visited_urls)} sitemaps and found {len(all_urls)} unique URLs"
            )
            return all_urls

        # Start the recursive process and return results
        return _build_tree_recursive(root_node)
