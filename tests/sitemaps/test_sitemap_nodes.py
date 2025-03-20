import pytest

from ethicrawl.context import Context
from ethicrawl.core import Resource
from ethicrawl.sitemaps import (
    IndexNode,
    IndexEntry,
    SitemapNode,
    UrlsetNode,
    UrlsetEntry,
)
from ethicrawl.sitemaps.sitemap_error import SitemapError


html_doc = """
<html xmlns="http://www.w3.org/TR/html4/">
    <head>
        <title>Test Document</title>
    </head>
    <body>
        <h1>Hello World!</h1>
    </body>
</html>
"""

malformed_doc = """
<html xmlns="http://www.w3.org/TR/html4/">
    <head>
        <title>Test Document</title>
    </head>
    <body>
        <h1>Hello World!</p>
        <p>Foo Bar</h1>
    </body>
</html>
"""

urlset_doc = """
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
    <url>
        <loc>https://www.example.com/sport</loc>
        <changefreq>hourly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://www.example.com/sport/football</loc>
        <changefreq>hourly</changefreq>
        <priority>0.8</priority>
        <lastmod>2025-03-03</lastmod>
    </url>
    <url>
        <changefreq>hourly</changefreq>
        <priority>0.8</priority>
        <lastmod>2025-03-03</lastmod>
    </url>
</urlset>"""

index_doc = """
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <sitemap>
        <loc>https://www.example.com/sport/sitemap.xml</loc>
        <lastmod>2025-03-03</lastmod>
    </sitemap>
    <sitemap>
        <foo>bar</foo>
    </sitemap>
</sitemapindex>
"""

invalid_sitemap_doc = """
<foo xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
    <bar>baz</bar>
</foo>
"""


class TestSitemapNode:
    def get_context(self) -> Context:
        url = "https://www.example.com/sitemap.xml"
        return Context(Resource(url))

    def test_wrong_namespace(self):
        with pytest.raises(
            SitemapError,
            match="Invalid XML syntax: Required default namespace not found: http://www.sitemaps.org/schemas/sitemap/0.9",
        ):
            node = SitemapNode(self.get_context(), html_doc)

    def test_malformed_doc(self):
        with pytest.raises(
            SitemapError,
            match="Invalid XML syntax.*",
        ):
            node = SitemapNode(self.get_context(), malformed_doc)


class TestIndexNode(TestSitemapNode):
    def test_index(self):
        # Create index node
        node = IndexNode(self.get_context(), index_doc)

        assert node.type == "sitemapindex"

        assert len(node.entries) == 1
        assert all(isinstance(entry, IndexEntry) for entry in node.entries)

        # Verify first entry
        first = node.entries[0]
        assert first.url == "https://www.example.com/sport/sitemap.xml"
        assert first.lastmod == "2025-03-03"

    def test_bad_index(self):
        """Test handling of malformed urlset (correct namespace but wrong structure)."""

        # Create node with badly structured but valid XML
        with pytest.raises(ValueError, match="Expected a root sitemapindex got foo"):
            node = IndexNode(self.get_context(), invalid_sitemap_doc)

    def test_index_setter(self):
        node = IndexNode(self.get_context())
        entry = IndexEntry("https://www.example.com/sport/sitemap.xml")
        with pytest.raises(TypeError, match="Expected a list, got int"):
            node.entries = 1
        with pytest.raises(TypeError, match="Expected IndexEntry, got int"):
            node.entries = [entry, 1]
        node.entries = [entry]
        assert node.entries[-1].url == "https://www.example.com/sport/sitemap.xml"


class TestUrlSetNode(TestSitemapNode):
    def test_urlset(self):
        # Create urlset node
        node = UrlsetNode(self.get_context(), urlset_doc)

        # Verify node type
        assert node.type == "urlset"

        # Verify entries are parsed
        assert len(node.entries) == 2
        assert all(isinstance(entry, UrlsetEntry) for entry in node.entries)

        # Verify first entry
        first = node.entries[0]
        assert str(first.url) == "https://www.example.com/sport"
        assert first.changefreq == "hourly"
        assert first.priority == 0.8
        assert first.lastmod is None

        # Verify second entry
        second = node.entries[1]
        assert str(second.url) == "https://www.example.com/sport/football"
        assert second.changefreq == "hourly"
        assert second.priority == 0.8
        assert second.lastmod == "2025-03-03"

        # Test string representation
        assert "UrlsetNode" in str(node)

    def test_bad_urlset(self):
        """Test handling of malformed urlset (correct namespace but wrong structure)."""

        # Create node with badly structured but valid XML
        with pytest.raises(ValueError, match="Expected a root urlset got foo"):
            node = UrlsetNode(self.get_context(), invalid_sitemap_doc)
