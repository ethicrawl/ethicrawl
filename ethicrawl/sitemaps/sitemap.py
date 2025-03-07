# ethicrawl/sitemaps/sitemap.py
from typing import List, Optional, Union, Pattern
import re
from ethicrawl.config.config import Config
from ethicrawl.client import HttpClient
from ethicrawl.sitemaps.sitemap_urls import SitemapUrlsetUrl
from ethicrawl.sitemaps.node_factory import NodeFactory
from ethicrawl.sitemaps.sitemap_nodes import IndexNode, UrlsetNode
from ethicrawl.sitemaps.sitemap_result import SitemapResult

from ethicrawl.core import EthicrawlContext


class Sitemap:
    """Builds sitemap trees and extracts URLs."""

    def __init__(self, context: EthicrawlContext, url_filter: Optional[str] = None):
        """
        Initialize the sitemap processor.

        Args:
            context: Ethicrawl context with HTTP client and base URL
            url_filter: Optional regex pattern to filter top-level sitemaps
        """
        self._context = context
        self._logger = self._context.logger("sitemap")
        self._url_filter = re.compile(url_filter) if url_filter else None
        self._root_node = None

    def filter(self, pattern: str) -> "Sitemap":
        """
        Apply a filter pattern to the sitemaps.

        Args:
            pattern: Regex pattern to filter sitemap URLs

        Returns:
            self: For method chaining
        """
        self._url_filter = re.compile(pattern) if pattern else None
        return self  # Return self for chaining

    def from_robots(self) -> "Sitemap":
        """
        Use sitemaps discovered in robots.txt.

        Returns:
            self: For method chaining
        """
        # Get the robots_handler from the Ethicrawl instance
        # Normally we'd have a getter for this in EthicrawlContext
        # But we can access ec._robots_handler directly for now
        from ethicrawl.core.old_ethicrawl import Ethicrawl

        # Create a temporary Ethicrawl instance to get robots handler
        # This isn't ideal but works as a workaround
        ec = Ethicrawl(self._context.url, http_client=self._context.client)

        # Create an IndexNode with those sitemaps
        self._root_node = IndexNode(self._context)
        self._root_node.items = ec._robots_handler.sitemaps

        # Apply filter if set
        if self._url_filter and self._root_node.items:
            original_count = len(self._root_node.items)
            self._root_node.items = [
                item
                for item in self._root_node.items
                if self._url_filter.search(item.loc)
            ]
            filtered_count = len(self._root_node.items)

            if filtered_count < original_count:
                self._logger.info(
                    f"Filtered sitemaps with pattern '{self._url_filter.pattern}': "
                    f"{filtered_count}/{original_count} matched"
                )

        return self  # Return self for chaining

    def from_index(self, index: IndexNode) -> "Sitemap":
        """
        Use an existing sitemap index node.

        Args:
            index: Pre-populated IndexNode with sitemap URLs

        Returns:
            self: For method chaining
        """
        # Verify it's an IndexNode
        if not isinstance(index, IndexNode):
            raise TypeError("Expected IndexNode instance")

        self._root_node = index

        # Apply filter if set
        if self._url_filter and self._root_node.items:
            original_count = len(self._root_node.items)
            self._root_node.items = [
                item
                for item in self._root_node.items
                if self._url_filter.search(item.loc)
            ]
            filtered_count = len(self._root_node.items)

            if filtered_count < original_count:
                self._logger.info(
                    f"Filtered sitemaps with pattern '{self._url_filter.pattern}': "
                    f"{filtered_count}/{original_count} matched"
                )

        return self  # Return self for chaining

    def items(self, max_depth: int = 5) -> "SitemapResult":
        """
        Process sitemaps and return a filterable result object.

        Args:
            max_depth: Maximum recursion depth for processing sitemap indexes

        Returns:
            SitemapResult: Object containing URLs that can be further filtered

        Raises:
            ValueError: If no sitemap source is specified
        """
        if not self._root_node:
            raise ValueError("No sitemap source specified. Use from_robots() first.")

        # Process sitemaps using the existing implementation
        all_urls = self._process_sitemaps(self._root_node, max_depth)
        return SitemapResult(all_urls, self._context)

    def _process_sitemaps(
        self, root_node: IndexNode, max_depth: int = 5
    ) -> List[SitemapUrlsetUrl]:
        """
        Build a sitemap tree and return a flat list of all URLs.

        This is the implementation moved from the old items() method
        """
        # Initialize tracking set for cycle detection
        visited_urls = set()

        # Define the recursive implementation as an inner function
        def _build_tree_recursive(
            node: IndexNode, current_depth: int = 0
        ) -> List[SitemapUrlsetUrl]:
            all_urls = []

            # Check recursion depth
            if current_depth >= max_depth:
                self._logger.warning(
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
                        self._logger.debug(
                            f"Skipping already visited sitemap: {sitemap_url.loc}"
                        )
                        continue

                    self._logger.debug(f"Processing sitemap: {sitemap_url.loc}")

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
                    self._logger.warning(
                        f"Error processing sitemap URL {sitemap_url.loc}: {str(e)}"
                    )
                    continue

            self._logger.info(
                f"Visited {len(visited_urls)} sitemaps and found {len(all_urls)} unique URLs"
            )
            return all_urls

        # Start the recursive process and return results
        return _build_tree_recursive(root_node)
