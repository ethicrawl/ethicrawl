import urllib.parse
from ethicrawl.client.http_client import HttpClient
from ethicrawl.client.http_response import HttpResponse
from ethicrawl.robots.robots_handler import RobotsHandler
from ethicrawl.sitemaps import SitemapFactory
from typing import Optional, Union, Pattern
import socket


class EthiCrawl:
    @staticmethod
    def validate(url, scheme_netloc_only=False):
        try:
            _parsed = urllib.parse.urlparse(url)
            if _parsed.scheme not in ["http", "https"]:
                raise ValueError("Only HTTP(s) Supported")
            # Check if hostname resolves
            socket.gethostbyname(_parsed.netloc)
        except socket.gaierror:
            raise ValueError(f"Cannot resolve hostname: {_parsed.netloc}")
        if scheme_netloc_only:
            return _parsed.scheme + "://" + _parsed.netloc
        else:
            return url

    def __init__(self, base: str, http_client=None) -> None:
        """
        Initialize the site crawler with a base URL.

        Args:
            base (str): Base URL for the crawler (e.g., "https://example.com")
            http_client (HttpClient, optional): HTTP client to use for requests
        """
        # Set up HTTP clients
        self._lightweight_http_client = HttpClient()
        self._http_client = http_client or self._lightweight_http_client

        # Parse and validate the base URL
        print(base)
        self._base = self.validate(base)
        parsed_base = urllib.parse.urlparse(self._base)

        # Extract and store domain information
        self._base_domain = parsed_base.netloc
        self._base_scheme = parsed_base.scheme
        self._base_url = (
            f"{self._base_scheme}://{self._base_domain}"  # Clean base URL without path
        )

        # Initialize domain permissions
        self._allowed_domains = {self._base_domain: self._http_client}

        # Initialize robots handler for the main site
        self._robots_handler = RobotsHandler(self._http_client, self._base_url)

        # Get sitemaps

        # self._sitemaps = SitemapsHandler(
        #     self._http_client,
        #     self._base_url,
        #     self._robots_handler.get_sitemaps(),
        # )

        self._sitemaps = SitemapFactory.create_index(
            self._robots_handler.get_sitemaps()
        )

    def bind(self, url: str, http_client=None) -> bool:
        try:
            validated_url = self.validate(url)
            domain = urllib.parse.urlparse(validated_url).netloc
            self._allowed_domains[domain] = http_client or self._lightweight_http_client
            return True
        except ValueError:
            return False

    def get(self, url: str) -> HttpResponse:
        """Get content from a URL, handling relative and absolute URLs properly"""
        try:
            parsed_url = self._parse_url(url)

            # Check domain permissions
            domain = parsed_url.netloc
            if domain not in self._allowed_domains:
                raise ValueError(f"Domain not allowed: {domain}")

            # Get the appropriate client for this domain
            client = self._allowed_domains[domain]

            # Check robots.txt rules only for the main site domain
            if domain == self._base_domain:
                if not self._robots_handler.can_fetch(parsed_url.geturl()):
                    raise ValueError(
                        f"URL disallowed by robots.txt: {parsed_url.geturl()}"
                    )

            # Finally, fetch the response with the domain-specific client
            return client.get(parsed_url.geturl())
        except ValueError as e:
            raise

    def discover(
        self,
        pattern: Optional[Union[str, Pattern]] = None,
        fast: bool = False,
    ):
        """
        Discover sitemap URLs, optionally filtered by a pattern.

        Args:
            pattern (str or re.Pattern, optional):
                If provided, only return sitemaps matching this pattern:
                - String pattern uses 'in' operator for substring matching
                - Regex pattern uses pattern.search() for matching

        Returns:
            SitemapResult: Object containing discovered sitemap URLs

        Examples:
            # String pattern
            result = crawler.discover("_uk_en")

            # Regex pattern
            import re
            result = crawler.discover(re.compile(r'_uk_en|_us_en'))
        """
        # Simply proxy to the SitemapsHandler's discover method
        if fast:
            return self._robots_handler.get_sitemaps()
        else:
            return self._sitemaps.discover(pattern)

    def _parse_url(self, url: str) -> urllib.parse.ParseResult:
        """Parse and normalize a URL, handling relative URLs and validating format"""
        # Parse the URL without validation first
        parsed_url = urllib.parse.urlparse(url)

        # Check if this looks like a domain name without scheme
        if (
            not parsed_url.scheme
            and not parsed_url.netloc
            and ("." in url and "/" not in url)
        ):
            raise ValueError(
                f"Invalid URL: {url}. Missing scheme (http:// or https://)."
            )

        # Handle different URL types
        if not parsed_url.scheme and not parsed_url.netloc:
            # Relative URL
            if url.startswith("/"):
                # Absolute path
                full_url = f"{self._base_url}{url}"
            else:
                # Relative path
                base_path = urllib.parse.urlparse(self._base).path
                if base_path and not base_path.endswith("/"):
                    base_path = base_path.rsplit("/", 1)[0] + "/"
                full_url = f"{self._base_url}{base_path}{url}"
            parsed_url = urllib.parse.urlparse(full_url)

        return parsed_url
