from functools import wraps
from logging import Logger as logging_Logger
from typing import TypeVar, cast

from ethicrawl.client import Response
from ethicrawl.client.http import HttpClient, HttpResponse
from ethicrawl.config import Config
from ethicrawl.context import Context
from ethicrawl.error import DomainWhitelistError
from ethicrawl.core import Headers, Resource, Url
from ethicrawl.robots import Robot
from ethicrawl.sitemaps import SitemapParser

from .domain_context import DomainContext

T = TypeVar("T", bound=DomainContext)


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

    def _get_root_domain(self) -> DomainContext:
        """Get the root domain context with type safety.

        Returns:
            The root domain context

        Raises:
            RuntimeError: If the root domain is not set
        """
        if not hasattr(self, "_root_domain") or self._root_domain is None:
            raise RuntimeError("Root domain not initialized")
        return cast(DomainContext, self._root_domain)

    def bind(self, url: str | Url | Resource, client: HttpClient | None = None) -> bool:
        """Bind the ethicrawl to a specific website domain.

        Binding establishes the primary domain context with its robots.txt handler,
        client configuration, and sets up logging for operations on this domain.

        Args:
            url: The base URL of the site to crawl (string, Url, or Resource)
            client: HTTP client to use for requests. Defaults to a standard HttpClient

        Returns:
            bool: True if binding was successful

        Raises:
            ValueError: If URL is invalid
            RuntimeError: If already bound to a different site
        """
        if self.bound:
            root_domain = self._get_root_domain()
            raise RuntimeError(
                f"Already bound to {root_domain.context.resource.url} - unbind() first"
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
        """Unbind the ethicrawl from its current site.

        This releases resources and allows the ethicrawl to be bound to a different site.
        It removes all domain contexts, cached resources, and resets the ethicrawl state.

        Returns:
            bool: True if unbinding was successful
        """
        # Find all instance attributes starting with underscore
        if self.bound:
            domain = self._get_root_domain().context.resource.url.netloc
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

        # Include both scheme and netloc in the domain key
        domain_key = f"{url.scheme}://{url.netloc}"
        root_domain = self._get_root_domain()
        context = Context(Resource(url), client or root_domain.context.client)

        self._whitelist[domain_key] = DomainContext(context=context)
        self.logger.info("Whitelisted domain: %s", domain_key)
        return True

    @property
    def bound(self) -> bool:
        """Check if currently bound to a site.

        Returns:
            bool: True if the ethicrawl is bound to a domain, False otherwise
        """
        return hasattr(self, "_root_domain") and self._root_domain is not None

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
        root_domain = self._get_root_domain()
        return root_domain.context.logger("")

    @property
    @ensure_bound
    def robots(self) -> Robot:
        """Access the robots.txt handler for the bound domain.

        The Robot instance manages fetching, parsing, and enforcing
        robots.txt rules for the current domain.

        Returns:
            Robot: The robots.txt handler for this domain

        Raises:
            RuntimeError: If not bound to a site
        """
        root_domain = self._get_root_domain()
        return root_domain.robot

    @property
    @ensure_bound
    def sitemaps(self) -> SitemapParser:
        """Access the sitemap parser for the bound domain.

        The parser is created on first access and cached for subsequent calls.
        It provides methods to extract URLs from XML sitemaps.

        Returns:
            SitemapParser: Parser for handling XML sitemaps

        Raises:
            RuntimeError: If not bound to a site
        """
        if not hasattr(self, "_sitemap"):
            root_domain = self._get_root_domain()
            self._sitemap = SitemapParser(root_domain.context)
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

        # Get domain from URL
        target_domain_key = f"{resource.url.scheme}://{resource.url.netloc}"

        # Check if domain is allowed
        root_domain = self._get_root_domain()
        domain_ctx = (
            root_domain
            if resource.url.netloc == root_domain.context.resource.url.netloc
            and resource.url.scheme == root_domain.context.resource.url.scheme
            else self._whitelist.get(target_domain_key)
        )

        if domain_ctx is None:
            # Change this line to include scheme in the bound domain
            bound_domain_key = f"{root_domain.context.resource.url.scheme}://{root_domain.context.resource.url.netloc}"

            self.logger.warning(
                "Domain not allowed: %s (bound to %s)",
                target_domain_key,  # This already includes scheme+netloc
                bound_domain_key,  # Now this also includes scheme+netloc
            )

            raise DomainWhitelistError(
                str(resource.url),
                bound_domain_key,  # Pass the full scheme+netloc format
            )
        else:
            self.logger.debug("Using domain context for %s", target_domain_key)

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
