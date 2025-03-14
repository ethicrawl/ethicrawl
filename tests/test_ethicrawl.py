import pytest
from unittest.mock import patch, MagicMock, call
import logging

from ethicrawl.core.ethicrawl import Ethicrawl, ensure_bound
from ethicrawl.client.http_client import HttpClient
from ethicrawl.client.http_response import HttpResponse
from ethicrawl.core.url import Url
from ethicrawl.core.resource import Resource
from ethicrawl.config.config import Config


class TestEthicrawl:
    def setup_method(self):
        """Set up test fixtures."""
        # Reset config for consistent test results
        Config.reset()
        self.crawler = Ethicrawl()

    def teardown_method(self):
        """Clean up after each test."""
        # Ensure we unbind any resources
        if self.crawler.bound:
            self.crawler.unbind()
        Config.reset()

    def test_initialization(self):
        """Test basic initialization."""
        # Should not be bound by default
        assert not self.crawler.bound

    def test_bind_with_string_url(self):
        """Test binding with a URL string."""
        # Skip validation but use the real Url class
        with patch("ethicrawl.core.url.socket.gethostbyname"):  # Skip DNS validation
            result = self.crawler.bind("https://example.com")

            # Verify binding was successful
            assert result is True
            assert self.crawler.bound
            assert str(self.crawler._context.resource.url) == "https://example.com"

    def test_bind_with_url_object(self):
        """Test binding with a Url object."""
        url = Url("https://example.com")

        result = self.crawler.bind(url)
        assert result is True
        assert self.crawler.bound

    def test_bind_with_custom_client(self):
        """Test binding with a custom client."""
        custom_client = HttpClient()

        result = self.crawler.bind("https://example.com", custom_client)
        assert result is True
        assert self.crawler.bound
        # Verify the custom client was used
        assert self.crawler._context.client == custom_client

    def test_unbind(self):
        """Test unbinding from a site."""
        # First bind to a site
        self.crawler.bind("https://example.com")
        assert self.crawler.bound

        # Now unbind
        result = self.crawler.unbind()
        assert result is True
        assert not self.crawler.bound
        assert not hasattr(self.crawler, "_context")

    def test_ensure_bound_decorator(self):
        """Test the ensure_bound decorator functionality."""

        # Create a test class with decorated method
        class TestClass:
            def __init__(self):
                self.bound = False

            @ensure_bound
            def test_method(self):
                return "Success"

        instance = TestClass()

        # Should raise RuntimeError when not bound
        with pytest.raises(
            RuntimeError, match="Operation requires binding to a site first"
        ):
            instance.test_method()

        # Should work when bound
        instance.bound = True
        assert instance.test_method() == "Success"

    def test_property_access_not_bound(self):
        """Test accessing properties when not bound."""
        # Each of these properties should raise RuntimeError when not bound
        with pytest.raises(
            RuntimeError, match="Operation requires binding to a site first"
        ):
            _ = self.crawler.robots

        with pytest.raises(
            RuntimeError, match="Operation requires binding to a site first"
        ):
            _ = self.crawler.sitemaps

        with pytest.raises(
            RuntimeError, match="Operation requires binding to a site first"
        ):
            _ = self.crawler.logger

    def test_property_access_when_bound(self):
        """Test accessing properties when bound."""
        # Bind to a site
        with patch("ethicrawl.core.url.socket.gethostbyname"):
            self.crawler.bind("https://example.com")

        # Create and inject mock objects directly instead of patching constructors
        mock_robots = MagicMock()
        mock_sitemaps = MagicMock()

        # Replace private attributes that the properties use
        self.crawler._robots = mock_robots
        self.crawler._sitemaps = mock_sitemaps

        # Access the properties
        robots = self.crawler.robots
        sitemaps = self.crawler.sitemaps
        logger = self.crawler.logger

        # Verify we got the expected objects
        assert robots is mock_robots
        assert sitemaps is mock_sitemaps
        assert isinstance(logger, logging.Logger)

    def test_get_same_domain(self):
        """Test GET request to the same domain."""
        # Bind to a site
        with patch("ethicrawl.core.url.socket.gethostbyname"):  # Skip DNS validation
            self.crawler.bind("https://example.com")

            # Mock robots handler to allow everything
            mock_robots = MagicMock()
            mock_robots.can_fetch.return_value = True
            self.crawler._robots = mock_robots

            # Mock the client's get method
            mock_response = MagicMock(spec=HttpResponse)
            self.crawler._context.client.get = MagicMock(return_value=mock_response)

            # Make a GET request
            result = self.crawler.get("https://example.com/page")

            # Verify robots was checked
            mock_robots.can_fetch.assert_called_once()

            # Verify client was called
            self.crawler._context.client.get.assert_called_once()

            # Verify the response was returned
            assert result == mock_response

    def test_get_different_domain_not_whitelisted(self):
        """Test GET request to a non-whitelisted domain."""
        # Bind to a site
        self.crawler.bind("https://example.com")

        # Try to request a different domain
        with pytest.raises(ValueError, match="Domain not allowed"):
            self.crawler.get("https://another-domain.com/page")

    def test_get_different_domain_whitelisted(self):
        """Test GET request to a whitelisted domain."""
        # Bind to a site
        with patch("ethicrawl.core.url.socket.gethostbyname"):
            self.crawler.bind("https://example.com")

        # Add the domain to the whitelist with DNS validation skipped
        with patch("ethicrawl.core.url.socket.gethostbyname"):
            self.crawler.whitelist("https://cdn.example.net")

        # Create a mock robots handler that allows all requests
        mock_robots = MagicMock()
        mock_robots.can_fetch.return_value = True

        # Replace the robots handler in the whitelist
        self.crawler._whitelist["cdn.example.net"]["robots_handler"] = mock_robots

        # Mock the client's get method
        mock_response = MagicMock(spec=HttpResponse)
        self.crawler._whitelist["cdn.example.net"]["context"].client.get = MagicMock(
            return_value=mock_response
        )

        # Make the GET request
        result = self.crawler.get("https://cdn.example.net/asset.jpg")

        # Verify
        mock_robots.can_fetch.assert_called_once()
        assert result == mock_response

    def test_get_url_disallowed_by_robots(self):
        """Test GET request to a URL disallowed by robots.txt."""
        # Bind to a site
        self.crawler.bind("https://example.com")

        # Mock robots handler to disallow the URL
        mock_robots = MagicMock()
        mock_robots.can_fetch.return_value = False
        self.crawler._robots = mock_robots

        # Try to request a disallowed URL
        with pytest.raises(ValueError, match="URL disallowed by robots.txt"):
            self.crawler.get("https://example.com/admin")

        # Verify robots was checked
        assert mock_robots.can_fetch.called

    def test_whitelist_domain(self):
        """Test whitelisting a domain."""
        # Bind to a site
        with patch("ethicrawl.core.url.socket.gethostbyname"):  # Skip DNS validation
            self.crawler.bind("https://example.com")

            # Mock the whitelist functionality
            with patch(
                "ethicrawl.robots.robots_handler.RobotsHandler"
            ) as mock_robots_class:
                mock_robots = MagicMock()
                mock_robots_class.return_value = mock_robots

                # Whitelist another domain - with DNS validation skipped
                with patch("ethicrawl.core.url.socket.gethostbyname"):
                    result = self.crawler.whitelist("https://cdn.example.net")

                # Verify whitelisting was successful
                assert result is True
                assert "cdn.example.net" in self.crawler._whitelist
                assert "context" in self.crawler._whitelist["cdn.example.net"]
                assert "robots_handler" in self.crawler._whitelist["cdn.example.net"]

    def test_whitelist_with_robots_error(self):
        """Test whitelisting a domain with robots.txt error."""
        # Bind to a site
        with patch("ethicrawl.core.url.socket.gethostbyname"):
            self.crawler.bind("https://example.com")

        # Instead of mocking a specific logger instance, let's patch the logging module
        with patch("logging.Logger.warning") as mock_warning:
            # We'll patch the actual HTTP request that fetches robots.txt
            with patch(
                "ethicrawl.client.requests_transport.RequestsTransport.get"
            ) as mock_get:
                # Simulate HTTP error when fetching robots.txt
                mock_get.side_effect = Exception("Cannot fetch robots.txt")

                # Skip DNS validation for the whitelist operation
                with patch("ethicrawl.core.url.socket.gethostbyname"):
                    result = self.crawler.whitelist("https://cdn.example.net")

                # Verify whitelisting was successful
                assert result is True
                assert "cdn.example.net" in self.crawler._whitelist

                # Check that some warning was logged (we don't need to be too specific)
                assert mock_warning.called

    def test_get_with_resource(self):
        """Test GET request using a Resource object."""
        # Bind to a site
        self.crawler.bind("https://example.com")

        # Mock robots handler to allow everything
        mock_robots = MagicMock()
        mock_robots.can_fetch.return_value = True
        self.crawler._robots = mock_robots

        # Mock the client's get method
        mock_response = MagicMock(spec=HttpResponse)
        self.crawler._context.client.get = MagicMock(return_value=mock_response)

        # Create a Resource object
        resource = Resource("https://example.com/page")

        # Make a GET request with the Resource
        result = self.crawler.get(resource)

        # Verify client was called with the Resource
        self.crawler._context.client.get.assert_called_once_with(resource)

        # Verify the response was returned
        assert result == mock_response

    def test_get_invalid_url_type(self):
        """Test GET request with invalid URL type."""
        # Bind to a site
        self.crawler.bind("https://example.com")

        # Try to request with invalid type
        with pytest.raises(TypeError, match="Expected string, Url, or Resource"):
            self.crawler.get(123)  # Integer is not a valid URL type
