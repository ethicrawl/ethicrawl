import pytest
from unittest.mock import patch, MagicMock, call
import lxml.etree
import io

from ethicrawl.sitemaps.sitemaps import Sitemaps
from ethicrawl.sitemaps.sitemap_nodes import IndexNode, UrlsetNode
from ethicrawl.sitemaps.sitemap_util import SitemapType
from ethicrawl.core.context import Context
from ethicrawl.core.resource import Resource
from ethicrawl.core.resource_list import ResourceList
from ethicrawl.core.url import Url
from ethicrawl.config import Config


class TestSitemaps:
    def setup_method(self):
        """Set up test fixtures."""
        # Create a mock client
        self.mock_client = MagicMock()

        # Create a test resource
        self.resource = Resource("https://example.com")

        # Create a context
        with patch("ethicrawl.core.context.isinstance", return_value=True):
            self.context = Context(self.resource, self.mock_client)

        # Reset config for consistent test results
        Config.reset()

        # Create the sitemaps instance
        self.sitemaps = Sitemaps(self.context)

    def create_urlset_xml(self, urls):
        """Helper to create urlset XML."""
        # Fix namespace handling - use None as default namespace
        nsmap = {None: "http://www.sitemaps.org/schemas/sitemap/0.9"}
        root = lxml.etree.Element("urlset", nsmap=nsmap)

        for url_data in urls:
            url_elem = lxml.etree.SubElement(root, "url")
            loc = lxml.etree.SubElement(url_elem, "loc")
            loc.text = url_data.get("loc")

            if "lastmod" in url_data:
                lastmod = lxml.etree.SubElement(url_elem, "lastmod")
                lastmod.text = url_data.get("lastmod")

        # Create XML with proper declaration
        return lxml.etree.tostring(
            root, xml_declaration=True, pretty_print=True, encoding="UTF-8"
        ).decode("utf-8")

    def create_sitemapindex_xml(self, sitemaps):
        """Helper to create sitemap index XML."""
        # Fix namespace handling - use None as default namespace
        nsmap = {None: "http://www.sitemaps.org/schemas/sitemap/0.9"}
        root = lxml.etree.Element("sitemapindex", nsmap=nsmap)

        for sitemap_data in sitemaps:
            sitemap_elem = lxml.etree.SubElement(root, "sitemap")
            loc = lxml.etree.SubElement(sitemap_elem, "loc")
            loc.text = sitemap_data.get("loc")

            if "lastmod" in sitemap_data:
                lastmod = lxml.etree.SubElement(sitemap_elem, "lastmod")
                lastmod.text = sitemap_data.get("lastmod")

        # Create XML with proper declaration
        return lxml.etree.tostring(
            root, xml_declaration=True, pretty_print=True, encoding="UTF-8"
        ).decode("utf-8")

    def test_initialization(self):
        """Test initialization of Sitemaps."""
        assert self.sitemaps._context == self.context
        assert self.sitemaps._logger is not None

    def test_parse_with_resource_list(self):
        """Test parsing a list of resources."""
        # Create resources
        resources = [
            Resource("https://example.com/sitemap1.xml"),
            Resource("https://example.com/sitemap2.xml"),
        ]

        # Create mock responses
        urlset1 = self.create_urlset_xml(
            [
                {"loc": "https://example.com/page1.html"},
                {"loc": "https://example.com/page2.html"},
            ]
        )

        urlset2 = self.create_urlset_xml(
            [
                {"loc": "https://example.com/page3.html"},
                {"loc": "https://example.com/page4.html"},
            ]
        )

        # Setup mock client responses
        mock_response1 = MagicMock()
        mock_response1.text = urlset1

        mock_response2 = MagicMock()
        mock_response2.text = urlset2

        self.mock_client.get.side_effect = [mock_response1, mock_response2]

        # Parse the sitemaps
        result = self.sitemaps.parse(resources)

        # Check the results
        assert len(result) == 4
        assert any(
            str(entry.url) == "https://example.com/page1.html" for entry in result
        )
        assert any(
            str(entry.url) == "https://example.com/page2.html" for entry in result
        )
        assert any(
            str(entry.url) == "https://example.com/page3.html" for entry in result
        )
        assert any(
            str(entry.url) == "https://example.com/page4.html" for entry in result
        )

    def test_parse_with_indexnode(self):
        """Test parsing with an IndexNode."""
        # Create an IndexNode
        index_node = IndexNode(self.context)

        # Use IndexEntry objects instead of Resource objects
        from ethicrawl.sitemaps.sitemap_entries import IndexEntry

        index_node.entries = [
            IndexEntry(Url("https://example.com/sub1.xml")),
            IndexEntry(Url("https://example.com/sub2.xml")),
        ]

        # Create mock responses
        urlset1 = self.create_urlset_xml(
            [
                {"loc": "https://example.com/page1.html"},
                {"loc": "https://example.com/page2.html"},
            ]
        )

        urlset2 = self.create_urlset_xml(
            [
                {"loc": "https://example.com/page3.html"},
                {"loc": "https://example.com/page4.html"},
            ]
        )

        # Setup mock client responses
        mock_response1 = MagicMock()
        mock_response1.text = urlset1

        mock_response2 = MagicMock()
        mock_response2.text = urlset2

        self.mock_client.get.side_effect = [mock_response1, mock_response2]

        # Parse the sitemaps
        result = self.sitemaps.parse(index_node)

        # Check the results
        assert len(result) == 4
        urls = [str(entry.url) for entry in result]
        assert "https://example.com/page1.html" in urls
        assert "https://example.com/page2.html" in urls
        assert "https://example.com/page3.html" in urls
        assert "https://example.com/page4.html" in urls

    def test_parse_nested_sitemaps(self):
        """Test parsing nested sitemaps (index -> index -> urlset)."""
        # Create resources
        resources = [Resource("https://example.com/sitemap_index.xml")]

        # Create mock responses: index -> sub-indexes -> urlsets
        sitemap_index = self.create_sitemapindex_xml(
            [
                {"loc": "https://example.com/subindex1.xml"},
                {"loc": "https://example.com/subindex2.xml"},
            ]
        )

        subindex1 = self.create_sitemapindex_xml(
            [{"loc": "https://example.com/urlset1.xml"}]
        )

        subindex2 = self.create_sitemapindex_xml(
            [{"loc": "https://example.com/urlset2.xml"}]
        )

        urlset1 = self.create_urlset_xml(
            [
                {"loc": "https://example.com/page1.html"},
                {"loc": "https://example.com/page2.html"},
            ]
        )

        urlset2 = self.create_urlset_xml(
            [
                {"loc": "https://example.com/page3.html"},
                {"loc": "https://example.com/page4.html"},
            ]
        )

        # Setup mock client responses
        self.mock_client.get.side_effect = [
            # First level
            MagicMock(text=sitemap_index),
            # Second level
            MagicMock(text=subindex1),
            MagicMock(text=subindex2),
            # Third level
            MagicMock(text=urlset1),
            MagicMock(text=urlset2),
        ]

        # Parse the sitemaps
        result = self.sitemaps.parse(resources)

        # Check the results
        assert len(result) == 4
        urls = [str(entry.url) for entry in result]
        assert "https://example.com/page1.html" in urls
        assert "https://example.com/page2.html" in urls
        assert "https://example.com/page3.html" in urls
        assert "https://example.com/page4.html" in urls

    def test_max_depth_limit(self):
        """Test max depth limit is respected."""
        # Set max depth to 0 to prevent any fetching
        config = Config()
        config.sitemap.max_depth = 0

        # Create resources
        resources = [Resource("https://example.com/sitemap_index.xml")]

        # Create mock response that should never be used
        sitemap_index = self.create_sitemapindex_xml(
            [{"loc": "https://example.com/subindex1.xml"}]
        )
        self.mock_client.get.return_value = MagicMock(text=sitemap_index)

        # Parse the sitemaps - should stop immediately due to depth 0
        result = self.sitemaps.parse(resources)

        # Check that NO requests were made - depth limit prevented any fetching
        assert self.mock_client.get.call_count == 0

        # Verify we got an empty result
        assert isinstance(result, ResourceList)
        assert len(result) == 0

    def test_cycle_detection(self):
        """Test cycle detection in sitemap references."""
        # Create resources
        resources = [Resource("https://example.com/sitemap_index.xml")]

        # Create cyclic references: index1 -> index2 -> index1
        sitemap_index1 = self.create_sitemapindex_xml(
            [{"loc": "https://example.com/subindex2.xml"}]
        )

        sitemap_index2 = self.create_sitemapindex_xml(
            [{"loc": "https://example.com/sitemap_index.xml"}]  # Cycle back to index1
        )

        # Setup mock client responses
        self.mock_client.get.side_effect = [
            MagicMock(text=sitemap_index1),
            MagicMock(text=sitemap_index2),
            # The third call would be a cycle, but should never happen
        ]

        # Parse the sitemaps - should handle the cycle without infinite recursion
        result = self.sitemaps.parse(resources)

        # Should only make 2 requests, then detect the cycle
        assert self.mock_client.get.call_count == 2

    def test_invalid_xml(self):
        """Test handling of invalid XML."""
        # Create resources
        resources = [Resource("https://example.com/invalid.xml")]

        # Setup invalid XML response
        invalid_xml = "<not valid xml>"
        self.mock_client.get.return_value = MagicMock(text=invalid_xml)

        # We only need to check that the error message contains the main pattern
        with pytest.raises(ValueError) as excinfo:
            self.sitemaps.parse(resources)

        # Only check for the consistent part of the error message
        assert "Failed to parse sitemap XML" in str(excinfo.value)
        # Remove specific error message check since it varies
        # assert "Invalid XML syntax" in str(excinfo.value)

    def test_unknown_root_element(self):
        """Test handling of unknown root element."""
        # Create resources
        resources = [Resource("https://example.com/unknown.xml")]

        # Create XML with unknown root
        unknown_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <unknown xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <element>Test</element>
        </unknown>"""

        self.mock_client.get.return_value = MagicMock(text=unknown_xml)

        # Parse should raise ValueError
        with pytest.raises(ValueError, match="Unknown sitemap type"):
            self.sitemaps.parse(resources)
