from abc import ABC, abstractmethod
from typing import List, Optional
from lxml import etree

from lxml import html
from typing import List, Optional, Set
import lxml
import gzip
from ethicrawl.client import HttpClient


import lxml

from .sitemap_urls import SitemapIndexEntry, SitemapUrlsetEntry
from .sitemap_util import SitemapError, SitemapHelper, SitemapType
from .sitemap_nodes import SitemapNode, UrlsetNode, IndexNode

from ethicrawl.core.context import Context


class NodeFactory:
    """Factory for creating sitemap nodes of the appropriate type."""

    @staticmethod
    def _validate(context: Context, document: str) -> SitemapNode:
        """
        Validate a sitemap document and create the appropriate node type.

        Args:
            document: XML document as string

        Returns:
            A sitemap node of the appropriate type

        Raises:
            SitemapError: For invalid sitemap documents
        """
        # Validate the XML structure using SitemapNode
        root = SitemapNode.get_lxml(context, document=document)
        root_name = lxml.etree.QName(root.tag).localname

        if root_name == "urlset":
            return UrlsetNode(context, document)
        elif root_name == "sitemapindex":
            return IndexNode(context, document)
        else:
            raise SitemapError(f"Unsupported sitemap type: {root_name}")

    @staticmethod
    def create(context: Context, sitemap_url: SitemapIndexEntry) -> SitemapNode:
        """
        Create a sitemap node by fetching and parsing a remote URL.

        Args:
            sitemap_url: The SitemapIndexEntry to fetch
            http_client: HttpClient instance for making requests

        Returns:
            A sitemap node of the appropriate type

        Raises:
            SitemapError: For any errors during fetch or parse
        """
        logger = context.logger("sitemap.factory.create")
        try:
            # URL is already validated in the SitemapIndexEntry object
            url = sitemap_url

            # Fetch the sitemap
            response = context.client.get(url.loc)
            # logger = context.get_logger("sitemap")

            # Check for success
            if not response or response.status_code != 200:
                raise SitemapError(
                    f"Failed to fetch sitemap from {url}: {response.status_code if response else 'No response'}"
                )

            # Validate the XML structure using SitemapNode
            node = NodeFactory._validate(context, response.text)
            node.source_url = url
            return node

        except Exception as e:
            logger.error(f"Error creating sitemap from URL {sitemap_url.loc}: {str(e)}")
            raise SitemapError(
                f"Error creating sitemap from URL {sitemap_url.loc}: {str(e)}"
            )
