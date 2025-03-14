import pytest
from unittest.mock import MagicMock, patch
from ethicrawl.sitemaps.sitemap_nodes import SitemapNode, IndexNode, UrlsetNode
from ethicrawl.sitemaps.sitemap_util import SitemapError, SitemapType
from ethicrawl.sitemaps.sitemap_entries import IndexEntry, UrlsetEntry
from ethicrawl.core.context import Context
from ethicrawl.core.resource import Resource


class TestSitemapNode:
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.resource = Resource("https://example.com")
        self.mock_client = MagicMock()

        # Create a real Context with our mock client
        with patch("ethicrawl.core.context.isinstance", return_value=True):
            self.context = Context(self.resource, self.mock_client)

        # Mock logger
        self.mock_logger = MagicMock()
        self.context.logger = MagicMock(return_value=self.mock_logger)

    def test_initialization_without_document(self):
        """Test initialization without a document."""
        node = SitemapNode(self.context)

        assert node.entries == []
        assert node.type == SitemapType.UNDEFINED

    def test_initialization_with_valid_document(self):
        """Test initialization with a valid XML document."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.com/page1</loc>
            </url>
        </urlset>"""

        node = SitemapNode(self.context, xml)
        assert node._root is not None

    def test_initialization_with_invalid_namespace(self):
        """Test initialization with invalid namespace."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://wrong-namespace.org">
            <url>
                <loc>https://example.com/page1</loc>
            </url>
        </urlset>"""

        with pytest.raises(SitemapError, match="Required default namespace not found"):
            SitemapNode(self.context, xml)

    def test_initialization_with_malformed_xml(self):
        """Test initialization with malformed XML."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.com/page1</loc>
            <!-- Missing closing tag -->
        </urlset>"""

        with pytest.raises(SitemapError, match="Invalid XML syntax"):
            SitemapNode(self.context, xml)

    def test_unescaped_ampersands_handling(self):
        """Test handling of unescaped ampersands in XML."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.com/page?param1=value1&param2=value2</loc>
            </url>
        </urlset>"""

        node = SitemapNode(self.context, xml)
        assert node._root is not None


class TestIndexNode:
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.resource = Resource("https://example.com")
        self.mock_client = MagicMock()

        # Create a real Context with our mock client
        with patch("ethicrawl.core.context.isinstance", return_value=True):
            self.context = Context(self.resource, self.mock_client)

        # Mock logger
        self.mock_logger = MagicMock()
        self.context.logger = MagicMock(return_value=self.mock_logger)

    def test_initialization_without_document(self):
        """Test initialization without a document."""
        node = IndexNode(self.context)

        assert node.entries == []
        assert node.type == SitemapType.INDEX

    def test_initialization_with_valid_index(self):
        """Test initialization with a valid sitemap index."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <sitemap>
                <loc>https://example.com/sitemap1.xml</loc>
                <lastmod>2023-01-01</lastmod>
            </sitemap>
            <sitemap>
                <loc>https://example.com/sitemap2.xml</loc>
            </sitemap>
        </sitemapindex>"""

        node = IndexNode(self.context, xml)

        assert len(node.entries) == 2
        assert str(node.entries[0].url) == "https://example.com/sitemap1.xml"
        assert node.entries[0].lastmod == "2023-01-01"
        assert str(node.entries[1].url) == "https://example.com/sitemap2.xml"
        assert node.entries[1].lastmod is None

    def test_initialization_with_wrong_root_element(self):
        """Test initialization with wrong root element type."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.com/page1</loc>
            </url>
        </urlset>"""

        with pytest.raises(ValueError, match="Expected a root sitemapindex got urlset"):
            IndexNode(self.context, xml)

    def test_entries_setter_with_valid_entries(self):
        """Test setting entries with valid entries."""
        node = IndexNode(self.context)

        entries = [
            IndexEntry("https://example.com/sitemap1.xml"),
            IndexEntry("https://example.com/sitemap2.xml"),
        ]

        node.entries = entries
        assert len(node.entries) == 2
        assert str(node.entries[0].url) == "https://example.com/sitemap1.xml"

    def test_entries_setter_with_invalid_type(self):
        """Test setting entries with invalid type."""
        node = IndexNode(self.context)

        with pytest.raises(TypeError, match="Expected a list"):
            node.entries = "not a list"

    def test_entries_setter_with_invalid_entries(self):
        """Test setting entries with invalid entry types."""
        node = IndexNode(self.context)

        entries = [IndexEntry("https://example.com/sitemap1.xml"), "not an IndexEntry"]

        with pytest.raises(TypeError, match="Expected IndexEntry"):
            node.entries = entries


class TestUrlsetNode:
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.resource = Resource("https://example.com")
        self.mock_client = MagicMock()

        # Create a real Context with our mock client
        with patch("ethicrawl.core.context.isinstance", return_value=True):
            self.context = Context(self.resource, self.mock_client)

        # Mock logger
        self.mock_logger = MagicMock()
        self.context.logger = MagicMock(return_value=self.mock_logger)

    def test_initialization_without_document(self):
        """Test initialization without a document."""
        node = UrlsetNode(self.context)

        assert node.entries == []
        assert node.type == SitemapType.URLSET

    def test_initialization_with_valid_urlset(self):
        """Test initialization with a valid sitemap urlset."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.com/page1</loc>
                <lastmod>2023-01-01</lastmod>
                <changefreq>daily</changefreq>
                <priority>0.8</priority>
            </url>
            <url>
                <loc>https://example.com/page2</loc>
            </url>
        </urlset>"""

        node = UrlsetNode(self.context, xml)

        assert len(node.entries) == 2
        assert str(node.entries[0].url) == "https://example.com/page1"
        assert node.entries[0].lastmod == "2023-01-01"
        assert node.entries[0].changefreq == "daily"
        assert node.entries[0].priority == 0.8
        assert str(node.entries[1].url) == "https://example.com/page2"
        assert node.entries[1].lastmod is None

    def test_initialization_with_wrong_root_element(self):
        """Test initialization with wrong root element type."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <sitemap>
                <loc>https://example.com/sitemap1.xml</loc>
            </sitemap>
        </sitemapindex>"""

        with pytest.raises(ValueError, match="Expected a root urlset got sitemapindex"):
            UrlsetNode(self.context, xml)

    def test_urlset_with_missing_loc_element(self):
        """Test urlset with a url missing the loc element."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.com/page1</loc>
            </url>
            <url>
                <!-- Missing loc element -->
                <lastmod>2023-01-01</lastmod>
            </url>
            <url>
                <loc>https://example.com/page3</loc>
            </url>
        </urlset>"""

        node = UrlsetNode(self.context, xml)
        # Should only have the two URLs with loc elements
        assert len(node.entries) == 2
        assert str(node.entries[0].url) == "https://example.com/page1"
        assert str(node.entries[1].url) == "https://example.com/page3"

    def test_urlset_with_invalid_entry(self):
        """Test urlset with an invalid entry that causes a ValueError."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.com/page1</loc>
            </url>
            <url>
                <loc>https://example.com/page2</loc>
                <priority>invalid</priority>
            </url>
            <url>
                <loc>https://example.com/page3</loc>
            </url>
        </urlset>"""

        # Invalid priority should be caught and logged, but not fail the parsing
        node = UrlsetNode(self.context, xml)
        # Should only have the two valid URLs
        assert len(node.entries) == 2
        urls = [str(entry.url) for entry in node.entries]
        assert "https://example.com/page1" in urls
        assert "https://example.com/page3" in urls
        # The error should be logged
        assert self.mock_logger.warning.called
