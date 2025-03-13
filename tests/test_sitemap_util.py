import pytest
from ethicrawl.sitemaps.sitemap_util import SitemapType, SitemapError, SitemapHelper


class TestSitemapType:
    def test_enum_values(self):
        """Test that enum values are correctly defined."""
        assert SitemapType.INDEX.value == "sitemapindex"
        assert SitemapType.URLSET.value == "urlset"
        assert SitemapType.UNDEFINED.value == "undefined"

    def test_enum_comparison(self):
        """Test comparing enum values."""
        assert SitemapType.INDEX == SitemapType.INDEX
        assert SitemapType.INDEX != SitemapType.URLSET
        assert SitemapType.INDEX != SitemapType.UNDEFINED


class TestSitemapError:
    def test_exception_raising(self):
        """Test that SitemapError can be raised and caught."""
        with pytest.raises(SitemapError) as excinfo:
            raise SitemapError("Test error message")

        assert "Test error message" in str(excinfo.value)

    def test_exception_inheritance(self):
        """Test that SitemapError inherits from Exception."""
        error = SitemapError("Test")
        assert isinstance(error, Exception)


class TestSitemapHelper:
    def test_validate_url_valid_cases(self):
        """Test URL validation with valid URLs."""
        # Test standard URLs
        valid_urls = [
            "https://example.com",
            "http://example.org/path",
            "https://sub.domain.com/page?param=value",
            "http://example.com/path#fragment",
            "  https://example.com/with-whitespace  ",  # Should be trimmed
        ]

        for url in valid_urls:
            result = SitemapHelper.validate_url(url)
            assert result == url.strip()

    def test_validate_url_invalid_cases(self):
        """Test URL validation with invalid URLs."""
        # Test invalid URLs
        invalid_urls = [
            None,  # None value
            "",  # Empty string
            "example.com",  # Missing scheme
            "https://",  # Missing netloc
            "invalid://",  # Invalid format
        ]

        for url in invalid_urls:
            with pytest.raises(ValueError):
                SitemapHelper.validate_url(url)

    def test_escape_unescaped_ampersands(self):
        """Test escaping unescaped ampersands in XML."""
        test_cases = [
            # Input, Expected Output
            ("no ampersands here", "no ampersands here"),
            ("one & ampersand", "one &amp; ampersand"),
            ("multiple & ampersands & here", "multiple &amp; ampersands &amp; here"),
            ("already escaped &amp; entity", "already escaped &amp; entity"),
            ("mixed & and &amp;", "mixed &amp; and &amp;"),
            ("other entities &#38; &#x26;", "other entities &#38; &#x26;"),
            (
                "complex case & with &amp; and &#38;",
                "complex case &amp; with &amp; and &#38;",
            ),
            ("a&b", "a&amp;b"),  # Adjacent to text
            ("a & b & c", "a &amp; b &amp; c"),
        ]

        for input_xml, expected_output in test_cases:
            result = SitemapHelper.escape_unescaped_ampersands(input_xml)
            assert result == expected_output

    def test_escape_unescaped_ampersands_with_complex_entities(self):
        """Test escaping with more complex XML entities."""
        xml = """<url>
            <loc>https://example.com/page?a=1&b=2</loc>
            <desc>Proper &amp; proper entities &lt; &gt; &#38;</desc>
        </url>"""

        expected = """<url>
            <loc>https://example.com/page?a=1&amp;b=2</loc>
            <desc>Proper &amp; proper entities &lt; &gt; &#38;</desc>
        </url>"""

        result = SitemapHelper.escape_unescaped_ampersands(xml)
        assert result == expected
