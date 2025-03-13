import pytest
from unittest.mock import MagicMock, patch
from ethicrawl.robots.robots_handler import RobotsHandler
from ethicrawl.core.context import Context
from ethicrawl.core.resource import Resource
from ethicrawl.core.url import Url


class TestRobotsHandler:
    def setup_method(self):
        """Set up test fixtures for each test method."""
        # Create a resource for the domain we're testing
        self.resource = Resource("https://example.com/page")

        # Create a real mock HTTP client
        self.mock_client = MagicMock()
        self.mock_client.user_agent = "test-bot"
        self.mock_client.__class__.__name__ = "HttpClient"
        self.mock_client.__class__.__module__ = "ethicrawl.client.http_client"

        # Create a real Context with our mock client
        with patch("ethicrawl.core.context.isinstance", return_value=True):
            self.context = Context(self.resource, self.mock_client)

        # Replace the logger with a mock for easier testing
        self.mock_logger = MagicMock()
        self.context.logger = MagicMock(return_value=self.mock_logger)

    def test_initialization(self):
        """Test basic initialization of the handler."""
        # Prepare mock response for robots.txt
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "User-agent: *\nDisallow: /private/"
        self.mock_client.get.return_value = mock_response

        # Create handler
        handler = RobotsHandler(self.context)

        # Verify robots.txt was fetched
        self.mock_client.get.assert_called_once()
        url_fetched = self.mock_client.get.call_args[0][0]
        assert str(url_fetched.url) == "https://example.com/robots.txt"

    def test_init_with_invalid_context(self):
        """Test initialization with invalid context."""
        with pytest.raises(ValueError):
            RobotsHandler("not-a-context")

    def test_user_agent_specific_rules(self):
        """Test that user-agent specific rules correctly override wildcard rules."""
        # Robots.txt with both wildcard and specific rules
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """User-agent: *
    Disallow: /private/

    User-agent: test-bot
    Disallow: /test-private/"""
        self.mock_client.get.return_value = mock_response

        # Create handler with test-bot user agent
        handler = RobotsHandler(self.context)

        # Test-bot can fetch /private/ (wildcard rule doesn't apply)
        assert handler.can_fetch("https://example.com/private/page")

        # Test-bot cannot fetch /test-private/ (specific rule applies)
        assert not handler.can_fetch("https://example.com/test-private/page")

        # Temporarily change user agent to wildcard
        original_ua = self.mock_client.user_agent
        self.mock_client.user_agent = "*"

        # Wildcard agent cannot fetch /private/ (wildcard rule applies)
        assert not handler.can_fetch("https://example.com/private/page")

        # Wildcard agent can fetch /test-private/ (specific rule doesn't apply)
        assert handler.can_fetch("https://example.com/test-private/page")

        # Restore original user agent
        self.mock_client.user_agent = original_ua

    def test_successful_robots_fetch(self):
        """Test fetching and parsing a valid robots.txt file."""
        # Prepare mock response with properly formatted robots.txt content
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """User-agent: *
    Disallow: /private/
    Allow: /public/

    User-agent: test-bot
    Disallow: /test-private/

    Sitemap: https://example.com/sitemap.xml"""
        self.mock_client.get.return_value = mock_response

        # Create handler
        handler = RobotsHandler(self.context)

        # Test permissions - CORRECTED expectations based on test-bot user agent:
        assert handler.can_fetch("https://example.com/public/page")

        # This is allowed for test-bot (even though it would be disallowed for *)
        # since the test-bot section doesn't mention /private/
        assert handler.can_fetch("https://example.com/private/page")

        # This is specifically disallowed for test-bot
        assert not handler.can_fetch("https://example.com/test-private/page")

        # Test sitemaps extraction
        sitemaps = handler.sitemaps
        assert len(sitemaps) == 1
        assert str(sitemaps[0].url) == "https://example.com/sitemap.xml"

    def test_missing_robots_txt(self):
        """Test handling of missing robots.txt (404)."""
        # Prepare mock 404 response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        self.mock_client.get.return_value = mock_response

        # Create handler
        handler = RobotsHandler(self.context)

        # All URLs should be allowed when robots.txt is missing
        assert handler.can_fetch("https://example.com/anything")
        assert handler.can_fetch("https://example.com/private/secret")

        # No sitemaps should be available
        assert len(handler.sitemaps) == 0

    def test_error_response_robots_txt(self):
        """Test handling of error response (403, 500, etc.)."""
        # Prepare mock error response
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        self.mock_client.get.return_value = mock_response

        # Create handler - should be conservative and block all
        handler = RobotsHandler(self.context)

        # All URLs should be blocked due to conservative approach
        assert not handler.can_fetch("https://example.com/anything")
        assert not handler.can_fetch("https://example.com/public/page")

    def test_exception_during_fetch(self):
        """Test handling of exceptions during robots.txt fetch."""
        # Make the get method raise an exception
        self.mock_client.get.side_effect = Exception("Network error")

        # Create handler - should handle exception gracefully
        handler = RobotsHandler(self.context)

        # Should be conservative and block all URLs
        assert not handler.can_fetch("https://example.com/anything")

    def test_can_fetch_with_different_input_types(self):
        """Test can_fetch with different input types (str, Url, Resource)."""
        # Prepare mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "User-agent: *\nDisallow: /private/"
        self.mock_client.get.return_value = mock_response

        # Create handler
        handler = RobotsHandler(self.context)

        # Test with different input types
        url_str = "https://example.com/public/page"
        url_obj = Url(url_str)
        resource_obj = Resource(url_obj)

        assert handler.can_fetch(url_str)
        assert handler.can_fetch(url_obj)
        assert handler.can_fetch(resource_obj)

        # Also test invalid input
        with pytest.raises(TypeError):
            handler.can_fetch(123)  # Not a valid URL type

    def test_sitemap_url_resolution(self):
        """Test sitemap URL resolution from relative to absolute paths."""
        # Prepare mock response with relative sitemap paths
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Remove leading spaces for proper parsing
        mock_response.text = """User-agent: *
Allow: /

Sitemap: https://example.com/sitemap1.xml
Sitemap: /sitemap2.xml
Sitemap: sitemap3.xml"""
        self.mock_client.get.return_value = mock_response

        # Create handler
        handler = RobotsHandler(self.context)

        # Test sitemap URL resolution
        sitemaps = handler.sitemaps
        assert len(sitemaps) == 3

        # Check that URLs are properly resolved
        sitemap_urls = [str(entry.url) for entry in sitemaps]
        assert "https://example.com/sitemap1.xml" in sitemap_urls
        assert "https://example.com/sitemap2.xml" in sitemap_urls
        assert "https://example.com/sitemap3.xml" in sitemap_urls
