from functools import wraps
from logging import Logger as logging_Logger

from ethicrawl.client import Response
from ethicrawl.client.http import HttpClient, HttpResponse
from ethicrawl.config import Config
from ethicrawl.context import Context
from ethicrawl.core import Headers, Resource, Url
from ethicrawl.robots import Robot
from ethicrawl.sitemaps import SitemapParser

from .domain_context import DomainContext


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
    """
    The main facade for ethicrawl operations.

    This class provides a simplified interface for crawling websites while respecting
    robots.txt rules, rate limits, and domain boundaries. It serves as the primary entry
    point for most users of the library.

    Examples:
        >>> from ethicrawl import Ethicrawl, HttpClient, Url
        >>> crawler = Ethicrawl()
        >>> client = HttpClient()
        >>> crawler.bind("https://example.com", client)
        >>> response = crawler.get("https://example.com/about")
        >>> print(response.status_code)
        200
        >>> crawler.unbind()  # Clean up when done

    Attributes:
        robots (RobotsHandler): Handler for robots.txt rules (available after binding)
        sitemap (SitemapParser): Parser and handler for XML sitemap (available after binding)
        logger (Logger): Logger for this crawler instance (available after binding)
        bound (bool): Whether the crawler is currently bound to a site
    """

    def bind(self, url: str | Url | Resource, client: HttpClient | None = None) -> bool:
        """
        Bind the crawler to a specific website domain.

        Args:
            url (str or Url): The base URL of the site to crawl
            client (HttpClient, optional): HTTP client to use for requests
                                        Defaults to a standard HttpClient

        Returns:
            bool: True if binding was successful, False otherwise

        Raises:
            ValueError: If URL is invalid
        """
        if self.bound:
            assert self._root_domain is not None
            raise RuntimeError(
                f"Already bound to {self._root_domain.context.resource.url} - unbind() first"
            )

        self._root_domain: DomainContext | None = None
        self._whitelist: dict[str, DomainContext] = {}

        if isinstance(url, Resource):
            url = url.url
        url = Url(str(url), validate=True)
        resource = Resource(url)
        client = client or HttpClient()
        context = Context(resource, client)

        # Use DomainContext for the root domain
        self._root_domain = DomainContext(context=context)
        self.logger.info("Successfully bound to %s", url)
        return True

    def unbind(self) -> bool:
        """
        Unbind the crawler from its current site.

        This releases resources and allows the crawler to be bound to a different site.

        Returns:
            Ethicrawl: Self for method chaining
        """
        # Find all instance attributes starting with underscore
        if self.bound:
            assert self._root_domain is not None
            domain = self._root_domain.context.resource.url.netloc
            self.logger.info("Unbinding from %s", domain)

        private_attrs = [attr for attr in vars(self) if attr.startswith("_")]

        # Delete each private attribute
        for attr in private_attrs:
            delattr(self, attr)

        # Verify unbinding was successful
        return not hasattr(self, "_root_domain")

    @ensure_bound
    def whitelist(self, url: str | Url, client: HttpClient | None = None) -> bool:
        """
        Whitelist an additional domain for crawling.

        By default, Ethicrawl will only request URLs from the bound domain.
        Whitelisting allows accessing resources from other domains (like CDNs).

        Args:
            url (str or Url): URL from the domain to whitelist
            client (HttpClient, optional): Client to use for this domain

        Returns:
            bool: True if whitelisting was successful

        Raises:
            RuntimeError: If not bound to a primary site
        """
        if isinstance(url, Resource):
            url = url.url
        url = Url(str(url), validate=True)

        domain = url.netloc
        assert self._root_domain is not None
        context = Context(Resource(url), client or self._root_domain.context.client)

        self._whitelist[domain] = DomainContext(context=context)
        self.logger.info("Whitelisted domain: %s", domain)
        return True

    @property
    def bound(self) -> bool:
        """Check if currently bound to a site."""
        return hasattr(self, "_root_domain") and self._root_domain is not None

    @property
    def config(self) -> Config:
        return Config()

    @property
    @ensure_bound
    def logger(self) -> logging_Logger:
        # Use the context from the root domain
        assert self._root_domain is not None
        return self._root_domain.context.logger("")

    @property
    @ensure_bound
    def robots(self) -> Robot:
        # Use the robot from the root domain
        assert self._root_domain is not None
        return self._root_domain.robot

    @property
    @ensure_bound
    def sitemaps(self) -> SitemapParser:
        if not hasattr(self, "_sitemap"):
            assert self._root_domain is not None
            self._sitemap = SitemapParser(self._root_domain.context)
        return self._sitemap

    @ensure_bound
    def get(
        self,
        url: str | Url | Resource,
        headers: Headers | dict | None = None,
    ) -> Response | HttpResponse:
        """
        Make an HTTP GET request to the specified URL, respecting robots.txt rules
        and domain whitelisting.

        Args:
            url (str, Url, or Resource): URL to fetch
            headers (dict, optional): Additional headers for this request

        Returns:
            HttpResponse: The response from the server

        Raises:
            ValueError: If URL is from a non-whitelisted domain or disallowed by robots.txt
            RuntimeError: If not bound to a site
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

        # Get domain from URL
        target_domain = resource.url.netloc

        # Check if domain is allowed
        assert self._root_domain is not None
        domain_ctx = (
            self._root_domain
            if target_domain == self._root_domain.context.resource.url.netloc
            else self._whitelist.get(target_domain)
        )

        if domain_ctx is None:
            # Fix incorrect curly brace string formatting
            self.logger.warning("Domain not allowed: %s", target_domain)
            raise ValueError(f"Domain not allowed: {target_domain}")
        else:
            self.logger.debug("Using domain context for %s", target_domain)

        context = domain_ctx.context
        robot = domain_ctx.robot

        # Extract User-Agent from headers if present (for robots.txt checking)
        user_agent = None
        if headers:
            headers = Headers(headers)
            user_agent = headers.get("User-Agent")

        # See if we can fetch the resource
        if robot.can_fetch(resource, user_agent=user_agent):
            self.logger.debug("Request permitted by robots.txt policy")

        # Use the domain's context to get its client
        if isinstance(context.client, HttpClient):
            return context.client.get(resource, headers=headers)
        return context.client.get(resource)
