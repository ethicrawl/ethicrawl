from lxml import html
from typing import List
import lxml

from ethicrawl.client import HttpClient
from ethicrawl.sitemaps.sitemap_util import SitemapError, SitemapHelper
from ethicrawl.sitemaps.sitemap_urls import SitemapIndexUrl
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
            url = sitemap_url.loc

            # Fetch the sitemap
            response = http_client.get(url)

            # Check for success
            if not response or response.status_code != 200:
                raise SitemapError(
                    f"Failed to fetch sitemap from {url}: {response.status_code if response else 'No response'}"
                )

            # Extract XML from browser-rendered response if needed
            document = SitemapFactory._extract_xml_from_chromium_response()

            # Validate the XML structure using SitemapNode
            return SitemapFactory._validate(document=document)

        except Exception as e:
            if isinstance(e, SitemapError):
                raise
            raise SitemapError(
                f"Error creating sitemap from URL {sitemap_url.loc}: {str(e)}"
            )

    @staticmethod
    def create_index(sitemap_urls: List[str], lastmod: str = "2025-03-01") -> IndexNode:
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
            return SitemapFactory._validate(document=document)

        except Exception as e:
            import traceback

            error_details = traceback.format_exc()
            if isinstance(e, SitemapError):
                raise
            raise SitemapError(
                f"Error creating sitemap index: {str(e)}\n{error_details}"
            )
