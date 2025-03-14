import pytest
from ethicrawl.core.url import Url
from unittest.mock import patch
import socket


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

    def test_url_extend_from_base_domain(self):
        """Test extending a base domain with a relative path."""
        # Test extending from domain with no trailing slash
        url = Url("https://example.com")
        extended = url.extend("path")
        assert str(extended) == "https://example.com/path"

        # Test chaining multiple extensions
        url = Url("https://example.com")
        extended = url.extend("path").extend("subpath")
        assert str(extended) == "https://example.com/path/subpath"

        # Test with domain that already has a path
        url = Url("https://example.com/existing")
        extended = url.extend("path")
        assert str(extended) == "https://example.com/existing/path"

    def test_http_only_decorator_on_file_url(self):
        """Test HTTP-only decorator raises exceptions for file:// URLs."""
        # Create a file URL
        file_url = Url("file:///home/user/document.txt")

        # Attempt to access HTTP-only properties
        with pytest.raises(ValueError, match="Only valid for HTTP and HTTPS urls"):
            _ = file_url.netloc

        with pytest.raises(ValueError, match="Only valid for HTTP and HTTPS urls"):
            _ = file_url.hostname

        with pytest.raises(ValueError, match="Only valid for HTTP and HTTPS urls"):
            _ = file_url.query_params

        # Test decorated method
        with pytest.raises(ValueError, match="Only valid for HTTP and HTTPS urls"):
            file_url._extend_with_params({"test": "value"})

    def test_url_validation_with_dns_lookup(self):
        """Test URL validation with DNS resolution."""
        # Valid hostname that should resolve
        valid_url = Url("https://google.com", validate=True)
        assert valid_url.hostname == "google.com"

        # Invalid hostname that won't resolve
        with pytest.raises(ValueError, match="Cannot resolve hostname"):
            Url("https://thisisanonexistentdomainforsure123.servfail", validate=True)

    def test_url_validation_with_dns_mock(self):
        """Test URL validation with mocked DNS resolution."""
        # Mock socket.gethostbyname to test both success and failure paths
        with patch("socket.gethostbyname") as mock_dns:
            # Successful resolution
            mock_dns.return_value = "192.168.1.1"
            valid_url = Url("https://example.com", validate=True)
            mock_dns.assert_called_once_with("example.com")

            # Failed resolution
            mock_dns.reset_mock()
            mock_dns.side_effect = socket.gaierror("Name does not resolve")
            with pytest.raises(ValueError, match="Cannot resolve hostname"):
                Url("https://invalid.example", validate=True)
            mock_dns.assert_called_once_with("invalid.example")

    def test_file_url_properties(self):
        """Test properties of file:// URLs."""
        url = Url("file:///home/user/document.txt")

        # Test basic properties
        assert url.scheme == "file"
        assert url.path == "/home/user/document.txt"
        assert url.base == "file://"

        # String representation
        assert str(url) == "file:///home/user/document.txt"

    def test_file_url_extend(self):
        """Test extending file:// URLs with paths."""
        url = Url("file:///home/user/")

        # Extend with relative path
        extended = url.extend("documents/report.pdf")
        assert str(extended) == "file:///home/user/documents/report.pdf"

        # Extend with absolute path
        extended = url.extend("/var/log/syslog")
        assert str(extended) == "file:///var/log/syslog"

        # Error case - query parameters not supported for file URLs
        with pytest.raises(
            ValueError, match="Query parameters are not supported for file:// URLs"
        ):
            url.extend({"param": "value"})

    def test_url_extend_edge_cases(self):
        """Test edge cases for URL extension."""
        # HTTP URL with no path
        url = Url("https://example.com")
        extended = url.extend("api")
        assert str(extended) == "https://example.com/api"

        # HTTP URL with existing path but no trailing slash
        url = Url("https://example.com/api")
        extended = url.extend("v1")
        assert str(extended) == "https://example.com/api/v1"

        # Invalid arguments
        url = Url("https://example.com")
        with pytest.raises(ValueError, match="Invalid arguments for extend()"):
            url.extend()  # No arguments

        with pytest.raises(ValueError, match="Invalid arguments for extend()"):
            url.extend(123)  # Invalid type

    def test_http_only_property_decorator(self):
        """Test the property decorator version of http_only."""
        from ethicrawl.core.url import http_only

        # Define a test class that uses http_only as a property decorator
        class TestClass:
            def __init__(self, url):
                from urllib.parse import urlparse

                self._parsed = urlparse(url)

            @property
            @http_only
            def test_property(self):
                """Test property that should only work for HTTP URLs."""
                return "Property value"

        # Test with HTTP URL - should work
        http_obj = TestClass("https://example.com")
        assert http_obj.test_property == "Property value"

        # Test with file URL - should fail
        file_obj = TestClass("file:///path/to/file")
        with pytest.raises(ValueError, match="Only valid for HTTP and HTTPS urls"):
            _ = file_obj.test_property

        # Now test the reverse order of decorators
        class ReverseTestClass:
            def __init__(self, url):
                from urllib.parse import urlparse

                self._parsed = urlparse(url)

            @http_only
            @property
            def test_property(self):
                """Test property with decorators in reverse order."""
                return "Property value"

        # Test with HTTP URL - should work
        http_obj = ReverseTestClass("https://example.com")
        assert http_obj.test_property == "Property value"

        # Test with file URL - should fail
        file_obj = ReverseTestClass("file:///path/to/file")
        with pytest.raises(ValueError, match="Only valid for HTTP and HTTPS urls"):
            _ = file_obj.test_property
