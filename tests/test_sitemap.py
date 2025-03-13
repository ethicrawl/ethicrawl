import pytest
from ethicrawl.core.url import Url


class TestUrl:
    """Tests for the Url class."""

    def test_url_initialization(self):
        """Test that Url objects can be created properly."""
        # Test with a valid HTTP URL
        url = Url("https://example.com/path?query=value#fragment")
        assert url.scheme == "https"
        assert url.netloc == "example.com"
        assert url.hostname == "example.com"
        assert url.path == "/path"
        assert url.query == "query=value"
        assert url.fragment == "fragment"
        assert url.query_params == {"query": "value"}
        assert str(url) == "https://example.com/path?query=value#fragment"

    def test_url_base(self):
        """Test the base property."""
        url = Url("https://example.com/path")
        assert url.base == "https://example.com"

    def test_url_equality(self):
        """Test URL equality comparison."""
        url1 = Url("https://example.com")
        url2 = Url("https://example.com")
        url3 = Url("https://example.org")

        assert url1 == url2
        assert url1 != url3
        assert url1 == "https://example.com"

    def test_invalid_url(self):
        """Test that invalid URLs raise appropriate exceptions."""
        with pytest.raises(ValueError):
            Url("invalid-url")

        with pytest.raises(ValueError):
            Url("ftp://example.com")  # Unsupported scheme

    def test_extend_path(self):
        """Test extending URLs with path components."""
        url = Url("https://example.com")
        extended = url.extend("path")
        assert str(extended) == "https://example.com/path"

        # Test extending with absolute path
        extended = url.extend("/absolute/path")
        assert str(extended) == "https://example.com/absolute/path"

    def test_extend_query_params(self):
        """Test extending URLs with query parameters."""
        url = Url("https://example.com")

        # Add parameters as dict
        extended = url.extend({"query": "value", "page": "1"})
        assert "query=value" in str(extended)
        assert "page=1" in str(extended)

        # Add parameters as key-value pair
        extended = url.extend("query", "value")
        assert str(extended) == "https://example.com?query=value"

    def test_file_url_handling(self):
        """Test handling of file:// URLs."""
        url = Url("file:///path/to/file")
        assert url.scheme == "file"
        assert url.path == "/path/to/file"
        assert url.base == "file://"

        # Extend with relative path
        extended = url.extend("subfile")
        assert str(extended) == "file:///path/to/file/subfile"

        # Test that query parameters are not supported for file URLs
        with pytest.raises(ValueError):
            url.extend({"query": "value"})
