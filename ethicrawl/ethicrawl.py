from functools import wraps
from logging import Logger as logging_Logger

from ethicrawl.client import Response, Client
from ethicrawl.client.http import HttpClient, HttpResponse
from ethicrawl.config import Config
from ethicrawl.context import Context
from ethicrawl.core import Headers, Resource, Url
from ethicrawl.robots import Robot
from ethicrawl.context import ContextManager
from ethicrawl.sitemaps import SitemapParser


def ensure_bound(func):
    """
    Decorator to ensure the Ethicrawl instance is bound to a site.

    Raises:
        RuntimeError: If the instance is not bound to a site
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.bound:
            raise RuntimeError(
                "Operation requires binding to a site first. "
                "Call bind(url, client) before using this method."
            )
        return func(self, *args, **kwargs)

    return wrapper


class Ethicrawl:
    """Main entry point for ethical web crawling operations.

    This class provides a simplified interface for crawling websites while respecting
    robots.txt rules, rate limits, and domain boundaries. It manages the lifecycle
    of crawling operations through binding to domains and provides access to robots.txt
    and sitemap functionality.

    Attributes:
        config (Config): Configuration settings for crawling behavior
        robots (Robot): Handler for robots.txt rules (available after binding)
        sitemaps (SitemapParser): Parser for XML sitemaps (available after binding)
        logger (Logger): Logger instance for this ethicrawl (available after binding)
        bound (bool): Whether the ethicrawl is currently bound to a site

    Example:
        >>> from ethicrawl import Ethicrawl
        >>> ethicrawl = Ethicrawl()
        >>> ethicrawl.bind("https://example.com")
        >>> response = ethicrawl.get("https://example.com/about")
        >>> print(response.status_code)
        200
        >>> # Find URLs in sitemap
        >>> urls = ethicrawl.sitemaps.parse()
        >>> ethicrawl.unbind()  # Clean up when done
    """

    def bind(self, url: str | Url | Resource, client: Client | None = None) -> bool:
        """Bind the ethicrawl to a specific website domain.

        Binding establishes the primary domain context with its robots.txt handler,
        client configuration, and sets up logging for operations on this domain.

        Args:
            url: The base URL of the site to crawl (string, Url, or Resource)
            client: HTTP client to use for requests. Defaults to a standard Client

        Returns:
            bool: True if binding was successful

        Raises:
            ValueError: If URL is invalid
            RuntimeError: If already bound to a different site
        """
        if isinstance(url, Resource):
            url = url.url
        url = Url(str(url), validate=True)
        resource = Resource(url)

        if not self.bound:
            self._context_manager: ContextManager = ContextManager()
            self._default_client: Client = client or HttpClient()
            self._context = Context(resource, self._default_client)

        client = client or self._default_client
        self._context_manager.bind(resource, client)
        self.logger.info("Successfully bound to %s", url)
        return True

    def unbind(self) -> bool:
        """Unbind the ethicrawl from its current site.

        This releases resources and allows the ethicrawl to be bound to a different site.
        It removes all domain contexts, cached resources, and resets the ethicrawl state.

        Returns:
            bool: True if unbinding was successful
        """
        # Find all instance attributes starting with underscore
        if self.bound:
            domain = self._context.resource.url.netloc
            self.logger.info("Unbinding from %s", domain)

        private_attrs = [attr for attr in vars(self) if attr.startswith("_")]

        # Delete each private attribute
        for attr in private_attrs:
            delattr(self, attr)

        # Verify unbinding was successful
        return not hasattr(self, "_root_domain")

    @ensure_bound
    def whitelist(self, url: str | Url, client: HttpClient | None = None) -> bool:
        """Add a domain to the whitelist.

        Deprecated:
            This method is deprecated and will be removed in a future version.
            Use bind() instead, which now serves the same purpose.

        Args:
            url: The base URL to whitelist
            client: HTTP client to use for this domain

        Returns:
            bool: True if whitelisting was successful
        """
        return self.bind(url, client)

    @property
    def bound(self) -> bool:
        """Check if currently bound to a site.

        Returns:
            bool: True if the ethicrawl is bound to a domain, False otherwise
        """
        return hasattr(self, "_context") and self._context is not None

    @property
    def config(self) -> Config:
        """Access the configuration settings for this ethicrawl.

        Returns:
            Config: The configuration object with settings for all ethicrawl components
        """
        return Config()

    @property
    @ensure_bound
    def logger(self) -> logging_Logger:
        """Get the logger for the current bound domain.

        This logger is configured according to the settings in Config.logger.

        Returns:
            Logger: Configured logger instance

        Raises:
            RuntimeError: If not bound to a site
        """
        return self._context.logger("")

    @property
    @ensure_bound
    def robots(self) -> Robot:
        return self._context_manager.robot(self._context.resource)

    @property
    @ensure_bound
    def sitemaps(self) -> SitemapParser:
        """Access the sitemap parser for the primary bound domain.

        The parser is created on first access and cached for subsequent calls.
        It provides methods to extract URLs from XML sitemaps.

        Returns:
            SitemapParser: Parser for handling XML sitemaps

        Raises:
            RuntimeError: If not bound to a site
        """

        if not hasattr(self, "_sitemap"):
            # Get a sitemap parser from the context manager that uses the correct client
            client = self._context_manager.client(self._context.resource)
            self._sitemap = self._context_manager.sitemap(self._context.resource)
        return self._sitemap

    @ensure_bound
    def get(
        self,
        url: str | Url | Resource,
        headers: Headers | dict | None = None,
    ) -> Response | HttpResponse:
        """Make an HTTP GET request to the specified URL, respecting robots.txt rules
        and domain whitelisting.

        This method enforces ethical crawling by:
        - Checking that the domain is allowed (primary or whitelisted)
        - Verifying the URL is permitted by robots.txt rules
        - Using the appropriate client for the domain

        Args:
            url: URL to fetch (string, Url, or Resource)
            headers: Additional headers for this request

        Returns:
            Response or HttpResponse: The response from the server

        Raises:
            ValueError: If URL is from a non-whitelisted domain or disallowed by robots.txt
            RuntimeError: If not bound to a site
            TypeError: If url parameter is not a string, Url, or Resource
        """
        # Handle different types of URL input
        if isinstance(url, Resource):
            resource = url
        elif isinstance(url, (str, Url)):
            resource = Resource(Url(str(url)))
        else:
            raise TypeError(
                f"Expected string, Url, or Resource, got {type(url).__name__}"
            )

        self.logger.debug("Preparing to fetch %s", resource.url)

        return self._context_manager.get(resource, headers=Headers(headers))
