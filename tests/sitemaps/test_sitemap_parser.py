import pytest
from unittest.mock import MagicMock, patch
from ethicrawl.sitemaps import (
    IndexNode,
    IndexEntry,
    UrlsetNode,
    SitemapParser,
)
from ethicrawl.context import Context
from ethicrawl.core import Resource, ResourceList
from ethicrawl.error import SitemapError

urlset_doc = """
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.sitemaps.org/schemas/sitemap/0.9">
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
<foo xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.sitemaps.org/schemas/sitemap/0.9">
    <bar>baz</bar>
</foo>
"""


class TestSitemapParser:
    def context(self) -> Context:
        url = "https://www.example.com/"
        return Context(Resource(url))

    def test_create_parser(self):
        context = self.context()
        sp = SitemapParser(context)

    def test_get_method(self):
        context = self.context()
        sp = SitemapParser(context)
        r = str(context.resource.url)

        with patch.object(context.client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = index_doc
            mock_get.return_value = mock_response
            result = sp._get(r)
            assert isinstance(result, IndexNode)

        with patch.object(context.client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = urlset_doc
            mock_get.return_value = mock_response
            result = sp._get(r)
            assert isinstance(result, UrlsetNode)

        with patch.object(context.client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = invalid_sitemap_doc
            mock_get.return_value = mock_response
            with pytest.raises(SitemapError):
                sp._get(r)

    def test_parse(self):
        """Test the parse method with different inputs."""
        context = self.context()
        parser = SitemapParser(context)

        # Mock the _traverse method to avoid actual traversal
        with patch.object(parser, "_traverse") as mock_traverse:
            # Set up mock to return a known value
            mock_traverse.return_value = []

            # Test parsing with an IndexNode
            index = IndexNode(context, index_doc)
            parser.parse(index)

            # Verify _traverse was called with the IndexNode and depth 0
            mock_traverse.assert_called_once_with(index, 0)

        # Test with a list of resources
        resources = [
            Resource("https://example.com/1"),
            Resource("https://example.com/2"),
        ]

        with patch.object(parser, "_traverse") as mock_traverse:
            mock_traverse.return_value = []
            parser.parse(resources)

            # Check that _traverse was called with a document containing our resources
            args = mock_traverse.call_args[0]
            document = args[0]

            assert isinstance(document, IndexNode)
            assert len(document.entries) == 2
            assert [str(e.url) for e in document.entries] == [
                "https://example.com/1",
                "https://example.com/2",
            ]

        # Test with a ResourceList directly

        resource_list = ResourceList(resources)

        with patch.object(parser, "_traverse") as mock_traverse:
            mock_traverse.return_value = []

            # Use the ResourceList we already created
            parser.parse(resource_list)

            # Check that _traverse was called with a document containing our resources
            args = mock_traverse.call_args[0]
            document = args[0]

            assert isinstance(document, IndexNode)
            assert len(document.entries) == 2
            assert [str(e.url) for e in document.entries] == [
                "https://example.com/1",
                "https://example.com/2",
            ]

        # Test with None input (default behavior)
        with patch.object(parser, "_traverse") as mock_traverse:
            mock_traverse.return_value = []

            # Call parse with no arguments
            parser.parse()

            # Check that _traverse was called with an empty document
            args = mock_traverse.call_args[0]
            document = args[0]

            assert isinstance(document, IndexNode)
            assert len(document.entries) == 0

    def test_process_entry_urlset(self):
        """Test processing an entry that contains a urlset document."""
        context = self.context()
        parser = SitemapParser(context)

        # Create an entry to process
        entry = IndexEntry("https://www.example.com/sitemap.xml")

        # Create a mock for _get to return a UrlsetNode
        with patch.object(parser, "_get") as mock_get:
            # Create a urlset node with our test document
            urlset = UrlsetNode(context, urlset_doc)
            mock_get.return_value = urlset

            # Call _process_entry
            visited = set()
            result = parser._process_entry(entry, 0, visited)

            # Verify the result contains the entries from the urlset
            assert len(result) == 2  # Only 2 valid entries with loc elements
            assert str(result[0].url) == "https://www.example.com/sport"
            assert str(result[1].url) == "https://www.example.com/sport/football"

            # Verify the URL was marked as visited
            assert "https://www.example.com/sitemap.xml" in visited

            # Verify _get was called with the right resource
            mock_get.assert_called_once()
            resource_arg = mock_get.call_args[0][0].url
            assert str(resource_arg) == "https://www.example.com/sitemap.xml"

    def test_process_entry_empty_urlset(self):
        """Test processing an entry that contains an empty urlset document."""
        context = self.context()
        parser = SitemapParser(context)
        entry = IndexEntry("https://www.example.com/empty.xml")

        # Create an empty urlset document
        empty_urlset_doc = """
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        </urlset>
        """

        # Mock _get to return an empty urlset
        with patch.object(parser, "_get") as mock_get:
            empty_urlset = UrlsetNode(context, empty_urlset_doc)
            mock_get.return_value = empty_urlset

            # Call _process_entry
            visited = set()
            result = parser._process_entry(entry, 0, visited)

            # Verify the result is empty
            assert len(result) == 0

            # Verify the URL was still marked as visited
            assert "https://www.example.com/empty.xml" in visited

    def test_process_entry_sitemapindex(self):
        """Test processing an entry that contains a sitemap index."""
        context = self.context()

        parser = SitemapParser(context)

        # Create an entry to process
        entry = IndexEntry("https://www.example.com/sitemapindex.xml")

        # Set up mocks for both _get and _traverse
        with patch.object(parser, "_get") as mock_get:
            with patch.object(parser, "_traverse") as mock_traverse:
                # Create an index node with our test document
                index_node = IndexNode(context, index_doc)
                mock_get.return_value = index_node

                # Make _traverse return some fake resources
                fake_resources = ResourceList(
                    [
                        Resource("https://www.example.com/page1"),
                        Resource("https://www.example.com/page2"),
                    ]
                )
                mock_traverse.return_value = fake_resources

                # Call _process_entry
                visited = set()
                current_depth = 2  # Test with non-zero depth to verify increment
                result = parser._process_entry(entry, current_depth, visited)

                # Verify result is what _traverse returned
                assert result is fake_resources

                # Verify URL was marked as visited
                assert "https://www.example.com/sitemapindex.xml" in visited

                # Verify _traverse was called with correct params
                mock_traverse.assert_called_once()
                args = mock_traverse.call_args[0]
                assert args[0] is index_node  # First arg should be the index node
                assert args[1] == current_depth + 1  # Depth should be incremented
                assert args[2] is visited  # Should use the same visited set

    def test_process_entry_cycle_detection(self):
        """Test that cycles are properly detected and handled."""
        context = self.context()
        parser = SitemapParser(context)

        # Create an entry to process
        url = "https://www.example.com/cycle.xml"
        entry = IndexEntry(url)

        # Create a visited set that already contains our URL
        visited = set([url])

        # Set up a mock for _get (which shouldn't be called)
        with patch.object(parser, "_get") as mock_get:
            # Call _process_entry
            result = parser._process_entry(entry, 0, visited)

            # Verify empty result
            assert len(result) == 0

            # Verify _get was not called
            mock_get.assert_not_called()

    def test_traverse_empty_index(self):
        context = self.context()
        parser = SitemapParser(context)
        empty_index = IndexNode(context)
        parser._traverse(empty_index)

    def test_traverse_empty_index_max_depth(self):
        context = self.context()
        parser = SitemapParser(context)
        empty_index = IndexNode(context)
        parser._traverse(empty_index, depth=2**1000)  # big number

    def test_traverse_entry_processing_loop(self):
        """Test the core entry processing loop in _traverse method."""
        context = self.context()
        parser = SitemapParser(context)

        # Create a node with specifically ordered entries
        node = IndexNode(context)
        node.entries = [
            IndexEntry("https://www.example.com/first"),
            IndexEntry("https://www.example.com/second"),
            IndexEntry("https://www.example.com/third"),
        ]

        # Track the exact order of entries processed and the accumulated results
        processed_entries = []

        # Mock _process_entry to track calls and return specific results
        with patch.object(parser, "_process_entry") as mock_process:

            def side_effect(item, depth, visited):
                # Record which entry was processed
                processed_entries.append(str(item.url))
                # Return different results based on the entry
                if "first" in str(item.url):
                    return ResourceList([Resource("https://www.example.com/result1")])
                elif "second" in str(item.url):
                    return ResourceList([])  # Test empty results handling
                else:
                    return ResourceList(
                        [
                            Resource("https://www.example.com/result3a"),
                            Resource("https://www.example.com/result3b"),
                        ]
                    )

            mock_process.side_effect = side_effect

            # Call _traverse
            result = parser._traverse(node, 1, {"already-visited"})

            # Verify all entries were processed in order
            assert processed_entries == [
                "https://www.example.com/first",
                "https://www.example.com/second",
                "https://www.example.com/third",
            ]

            # Verify correct parameters passed to _process_entry
            assert mock_process.call_count == 3
            for i, call in enumerate(mock_process.call_args_list):
                assert call[0][0] == node.entries[i]  # entry
                assert call[0][1] == 1  # depth
                assert "already-visited" in call[0][2]  # visited set

            # Verify results were accumulated correctly
            assert len(result) == 3
            assert str(result[0].url) == "https://www.example.com/result1"
            assert str(result[1].url) == "https://www.example.com/result3a"
            assert str(result[2].url) == "https://www.example.com/result3b"
