import pytest
import re
from logging import Logger as logging_Logger

from unittest.mock import Mock

from ethicrawl import Ethicrawl, Resource, Config, Url, HttpClient
from ethicrawl.robots import Robot
from ethicrawl.error import RobotDisallowedError, DomainWhitelistError
from ethicrawl.sitemaps import SitemapParser


class TestEthicrawl:
    def test_init_and_binding(self):
        """Test initialization and basic binding/unbinding"""
        crawler = Ethicrawl()

        # Test initial unbound state
        assert not crawler.bound

        # Test binding
        assert crawler.bind("https://example.com")
        assert crawler.bound
        assert hasattr(crawler, "_context")

        # Test unbinding
        assert crawler.unbind()
        assert not crawler.bound
        assert not hasattr(crawler, "_context")

        # Test binding with a Url
        assert crawler.bind(Url("https://example.com"))
        crawler.unbind()

        # Test binding with a Resource
        assert crawler.bind(Resource("https://example.com"))
        crawler.unbind()

    def test_ensure_bound_decorator(self):
        """Test the ensure_bound decorator prevents operations when unbound"""
        crawler = Ethicrawl()

        # Try operations before binding
        with pytest.raises(RuntimeError) as exc:
            crawler.whitelist("https://example2.com")
        assert "requires binding" in str(exc.value)

        with pytest.raises(RuntimeError) as exc:
            crawler.get("https://example.com/page")
        assert "requires binding" in str(exc.value)

    def test_singletons(self):
        crawler = Ethicrawl()
        crawler.bind("https://example.com")
        assert isinstance(crawler.logger, logging_Logger)
        assert isinstance(crawler.config, Config)

    def test_robot(self):
        crawler = Ethicrawl()
        crawler.bind("https://example.com")
        assert isinstance(crawler.robots, Robot)

    def test_sitemap(self):
        crawler = Ethicrawl()
        crawler.bind("https://example.com")
        assert isinstance(crawler.sitemaps, SitemapParser)

    def test_invalid_get(self):
        crawler = Ethicrawl()
        # from ethicrawl.client.client import NoneClient

        domain = "example.com"
        crawler.bind(f"https://{domain}")

        with pytest.raises(
            ValueError, match=re.escape("Only File and HTTP(S) URLs supported: foo")
        ):
            crawler.get("foo")
        with pytest.raises(
            TypeError,
            match=re.escape("Expected string, Url, or Resource, got int"),
        ):
            crawler.get(1)

    def test_get_with_real_server(self, test_server):
        """Test get method with a real HTTP server"""
        crawler = Ethicrawl()
        base_url = test_server

        # Bind to our test server
        crawler.bind(base_url)

        # Test different URL formats
        test_urls = [
            f"{base_url}/index.html",
            Resource(f"{base_url}/page1.html"),
            Url(f"{base_url}/page2.html"),
        ]

        for url in test_urls:
            result = crawler.get(url)
            assert result.status_code == 200
            assert "<html>" in result.text

        # Test the robots.txt was properly fetched
        assert crawler.robots is not None

    def test_robot_disallowed(self, test_server):
        """Test that robots.txt disallowed paths are enforced"""

        crawler = Ethicrawl()
        base_url = test_server

        # Create client with user agent directly specified
        headers = {"User-Agent": "BadBot"}
        client = HttpClient(headers=headers)

        # Bind to test server with our custom client
        crawler.bind(base_url, client=client)

        # Force robot initialization and print rules for debugging
        robot = crawler.robots
        print(f"User agent: {client.user_agent}")

        # Allowed path for BadBot should work
        result = crawler.get(f"{base_url}/public/page.html")
        assert result.status_code == 200

        # Disallowed path should raise RobotDisallowedError
        with pytest.raises(RobotDisallowedError):
            print(f"Testing disallowed path: {base_url}/private/secret.html")
            crawler.get(f"{base_url}/private/secret.html")

    def test_whitelist(self, test_server):
        """Test whitelisting additional domains for crawling"""
        crawler = Ethicrawl()

        # Extract the host and port from test_server URL
        from urllib.parse import urlparse

        parsed_url = urlparse(test_server)
        port = parsed_url.port or 5000

        # Bind to our main test server using localhost
        primary_url = f"http://localhost:{port}"
        crawler.bind(primary_url)

        # Whitelist the numeric IP representation - still the same server
        ip_url = f"http://127.0.0.1:{port}"
        assert crawler.whitelist(ip_url)

        # Test that requests to primary domain work
        result = crawler.get(f"{primary_url}/whitelist_test.html")
        assert result.status_code == 200
        assert "<html>" in result.text

        # Test that requests to whitelisted domain work (same server, different name)
        result = crawler.get(f"{ip_url}/whitelist_test.html")
        assert result.status_code == 200
        assert "<html>" in result.text

        # Test request to non-whitelisted domain is rejected
        with pytest.raises(
            DomainWhitelistError,
            match="Cannot access URL 'https://example.com/index.html' - domain not whitelisted.",
        ):
            crawler.get("https://example.com/index.html")

        # Check robot property accessor works
        robot = crawler.robots
        assert robot is not None

    def test_whitelist_resource(self):
        crawler = Ethicrawl()
        crawler.bind("https://example.com")
        crawler.whitelist(Resource("https://www.example.com"))

    def test_headers_and_user_agent(self, test_server):
        """Test that request headers and user-agent handling works properly"""
        from ethicrawl.core.headers import Headers

        crawler = Ethicrawl()
        base_url = test_server

        # Start with a crawler bound to a normal client
        client = HttpClient(headers={"User-Agent": "DefaultBot"})
        crawler.bind(base_url, client=client)

        # 1. Test with Headers object
        custom_headers = Headers({"User-Agent": "BadBot"})
        with pytest.raises(RobotDisallowedError):
            crawler.get(f"{base_url}/private/secret.html", headers=custom_headers)

        # 2. Test with regular dict with standard capitalization
        with pytest.raises(RobotDisallowedError):
            crawler.get(
                f"{base_url}/private/secret.html", headers={"User-Agent": "BadBot"}
            )

        # 3. Test with regular dict with non-standard capitalization
        with pytest.raises(RobotDisallowedError):
            crawler.get(
                f"{base_url}/private/secret.html", headers={"USER-agent": "BadBot"}
            )

        # 4. Test with fallback to client's default user-agent (which should be allowed)
        result = crawler.get(
            f"{base_url}/private/secret.html"
        )  # No headers, should use DefaultBot
        assert result.status_code == 200

        # 5. Test with overriding headers that don't include User-Agent
        result = crawler.get(
            f"{base_url}/private/secret.html", headers={"Accept": "text/html"}
        )
        assert result.status_code == 200  # Should still use DefaultBot

    def test_get_with_non_http_client(self):
        """Test the get method with a client that's not an HttpClient."""
        from ethicrawl.client.client import Client

        # Create a custom client that is not an HttpClient
        class CustomClient(Client):
            def __init__(self):
                self.get_called = False
                self.headers_passed = False

            def get(self, resource, **kwargs):
                self.get_called = True
                # Check if headers was passed (should not be in this case)
                self.headers_passed = "headers" in kwargs
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.text = "Custom client response"
                return mock_response

        crawler = Ethicrawl()
        custom_client = CustomClient()

        # Bind with custom client
        crawler.bind("https://example.com", client=custom_client)

        # Make a request - should call the custom client's get method without headers
        result = crawler.get("https://example.com/page", headers={"Custom": "Header"})

        # Verify the client's get was called
        assert custom_client.get_called is True

        # Verify that headers were NOT passed to the client's get method
        assert custom_client.headers_passed is False

        # Verify we got the expected response
        assert result.status_code == 200
        assert result.text == "Custom client response"
