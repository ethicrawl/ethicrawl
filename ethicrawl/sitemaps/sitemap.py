from lxml import html
from typing import List, Optional, Set
import lxml
import gzip
from ethicrawl.client import HttpClient
from ethicrawl.sitemaps.sitemap_util import SitemapError, SitemapHelper
from ethicrawl.sitemaps.sitemap_urls import SitemapIndexUrl, SitemapUrlsetUrl
from ethicrawl.sitemaps.sitemap_nodes import SitemapNode, IndexNode, UrlsetNode


class SitemapFactory:
    """Factory for creating sitemap nodes of the appropriate type."""

    @staticmethod
    def _extract_xml_from_chromium_response(content: bytes) -> str:
        """
        Extract XML content from a chromium-rendered XML page.

        Args:
            content: Raw response content from chromium

        Returns:
            str: Raw XML content or original content if no wrapper detected
        """

        content_str = content.decode("utf-8", errors="replace")

        # Check if this is a browser-rendered XML page
        if '<div id="webkit-xml-viewer-source-xml">' in content_str:
            try:
                # Parse HTML
                root = html.fromstring(content_str)

                # Extract content from the XML viewer div
                xml_div = root.xpath('//div[@id="webkit-xml-viewer-source-xml"]')
                if xml_div and len(xml_div) > 0:
                    # Get the XML content as string
                    xml_content = "".join(
                        lxml.etree.tostring(child, encoding="unicode")
                        for child in xml_div[0].getchildren()
                    )
                    return xml_content
            except Exception as e:
                print(f"Warning: Failed to extract XML from browser response: {e}")

        # Return original content if extraction failed
        return content_str

    @staticmethod
    def _validate(document: str) -> SitemapNode:
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
        root = SitemapNode.get_lxml(document=document)
        root_name = lxml.etree.QName(root.tag).localname

        if root_name == "urlset":
            return UrlsetNode(document)
        elif root_name == "sitemapindex":
            return IndexNode(document)
        else:
            raise SitemapError(f"Unsupported sitemap type: {root_name}")

    @staticmethod
    def create(sitemap_url: SitemapIndexUrl, http_client: HttpClient) -> SitemapNode:
        """
        Create a sitemap node by fetching and parsing a remote URL.

        Args:
            sitemap_url: The SitemapIndexUrl to fetch
            http_client: HttpClient instance for making requests

        Returns:
            A sitemap node of the appropriate type

        Raises:
            SitemapError: For any errors during fetch or parse
        """
        try:
            # URL is already validated in the SitemapIndexUrl object
            url = sitemap_url

            # Fetch the sitemap
            response = http_client.get(url.loc)

            # Check for success
            if not response or response.status_code != 200:
                raise SitemapError(
                    f"Failed to fetch sitemap from {url}: {response.status_code if response else 'No response'}"
                )

            # FIXME: Handle gzip sitemaps if the client hasn't already
            # if url.loc.lower().endswith(
            #     ".gz"
            # ) or "application/gzip" in response.headers.get("content-type"):
            #     try:
            #         content = gzip.decompress(response.content)
            #     except Exception as e:
            #         raise SitemapError(f"Failed to decompress gzipped sitemap {str(e)}")
            # else:
            #     content = response.content

            # Extract XML from browser-rendered response if needed
            document = SitemapFactory._extract_xml_from_chromium_response(
                response.content
            )

            # Validate the XML structure using SitemapNode
            node = SitemapFactory._validate(document=document)

            node.source_url = url

            return node

        except Exception as e:
            if isinstance(e, SitemapError):
                raise
            raise SitemapError(
                f"Error creating sitemap from URL {sitemap_url.loc}: {str(e)}"
            )

    @staticmethod
    def create_index(
        sitemap_urls: List[str], loc: str, lastmod: str = "2025-03-01"
    ) -> IndexNode:
        """
        Create a new SitemapIndexNode from a list of sitemap URLs.

        Args:
            sitemap_urls: List of sitemap URL strings
            lastmod: Optional lastmod date to use for all sitemaps

        Returns:
            SitemapIndexNode: A sitemap index containing the provided URLs

        Raises:
            SitemapError: If the sitemap generation fails
        """
        try:
            # Generate the sitemap XML directly as a string
            xml_lines = [
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            ]

            # Add each sitemap URL as an entry
            for url in sitemap_urls:
                try:
                    # Validate and normalize the URL
                    url = SitemapHelper.validate_url(url)
                    xml_lines.append("  <sitemap>")
                    xml_lines.append(f"    <loc>{url}</loc>")
                    if lastmod:
                        xml_lines.append(f"    <lastmod>{lastmod}</lastmod>")
                    xml_lines.append("  </sitemap>")
                except ValueError as e:
                    print(f"Skipping invalid URL: {e}")
                    continue

            # Close the root element
            xml_lines.append("</sitemapindex>")

            # Join into a single string
            document = "\n".join(xml_lines)

            # Validate and return the document
            node = SitemapFactory._validate(document=document)

            node.source_url = SitemapIndexUrl(loc=loc, lastmod=lastmod)

            return node

        except Exception as e:
            import traceback

            error_details = traceback.format_exc()
            if isinstance(e, SitemapError):
                raise
            raise SitemapError(
                f"Error creating sitemap index: {str(e)}\n{error_details}"
            )

    staticmethod

    def build_tree(
        root_node: IndexNode, http_client: HttpClient, max_depth: int = 5
    ) -> List[SitemapUrlsetUrl]:
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
        visited_urls = set()

        # Define the recursive implementation as an inner function
        def _build_tree_recursive(
            node: IndexNode, current_depth: int = 0
        ) -> List[SitemapUrlsetUrl]:
            all_urls = []

            # Check recursion depth
            if current_depth >= max_depth:
                print(
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
                        print(f"Skipping already visited sitemap: {sitemap_url.loc}")
                        continue

                    print(f"Processing sitemap: {sitemap_url.loc}")

                    # Mark this URL as visited
                    visited_urls.add(sitemap_url.loc)

                    # Fetch and parse this child sitemap
                    child_node = SitemapFactory.create(sitemap_url, http_client)

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
                    print(f"Error processing sitemap URL {sitemap_url.loc}: {str(e)}")
                    continue

            return all_urls

        # Start the recursive process and return results
        return _build_tree_recursive(root_node)
