from functools import wraps
from logging import Logger as logging_Logger
from typing import Union

from ethicrawl.context import Context
from ethicrawl.robots import Robot, RobotFactory
from ethicrawl.client.http import HttpClient, HttpResponse
from ethicrawl.core import Headers, Resource, Url
from ethicrawl.config import Config
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

    def __init__(self):
        pass

    def bind(self, url: Union[str, Url, Resource], client: HttpClient = None):
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
            raise RuntimeError(
                f"Already bound to {self._context.resource.url} - unbind() first"
            )
        if isinstance(url, Resource):
            url = url.url
        url = Url(str(url), validate=True)
        resource = Resource(url)
        client = client or HttpClient()
        self._context = Context(resource, client)
        return True if self._context is not None else False

    def unbind(self):
        """
        Unbind the crawler from its current site.

        This releases resources and allows the crawler to be bound to a different site.

        Returns:
            Ethicrawl: Self for method chaining
        """
        # Find all instance attributes starting with underscore
        private_attrs = [attr for attr in vars(self) if attr.startswith("_")]

        # Delete each private attribute
        for attr in private_attrs:
            delattr(self, attr)

        # Verify unbinding was successful
        return not hasattr(self, "_context")

    @ensure_bound
    def whitelist(self, url: Union[str, Url], client: HttpClient = None) -> bool:
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

        if not hasattr(self, "_whitelist"):
            self._whitelist = {}

        domain = url.netloc
        context = Context(Resource(url), client or self._context.client)

        robots_handler = RobotFactory.robot(context)

        self._whitelist[domain] = {"context": context, "robots_handler": robots_handler}
        self.logger.info(f"Whitelisted domain: {domain}")
        return True

    @property
    def bound(self) -> bool:
        """Check if currently bound to a site."""
        return hasattr(self, "_context")

    @property
    def config(self) -> Config:
        return Config()

    @property
    @ensure_bound
    def logger(self) -> logging_Logger:
        if not hasattr(self, "_logger"):
            self._logger = self._context.logger("")
        return self._logger

    @property
    @ensure_bound
    def robots(self) -> Robot:
        # lazy load robots
        if not hasattr(self, "_robots"):
            self._robot = RobotFactory.robot(self._context)
        return self._robot

    @property
    @ensure_bound
    def sitemaps(self) -> SitemapParser:
        if not hasattr(self, "_sitemap"):
            self._sitemap = SitemapParser(self._context)
        return self._sitemap

    @ensure_bound
    def get(
        self, url: Union[str, Url, Resource], headers: Union[Headers, dict] = None
    ) -> HttpResponse:
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

        # Get domain from URL
        target_domain = resource.url.netloc

        # Check if domain is allowed
        if target_domain == self._context.resource.url.netloc:
            # This is the main domain
            context = self._context
            robots_handler = self.robots
        elif hasattr(self, "_whitelist") and target_domain in self._whitelist:
            # This is a whitelisted domain
            context = self._whitelist[target_domain]["context"]
            robots_handler = self._whitelist[target_domain]["robots_handler"]
        else:
            # Log at WARNING level instead of just raising the exception
            self.logger.warning(f"Domain not allowed: {target_domain}")
            raise ValueError(f"Domain not allowed: {target_domain}")

        # Extract User-Agent from headers if present (for robots.txt checking)
        user_agent = None
        if headers:
            # Handle both Headers object and regular dict
            if isinstance(headers, Headers):
                user_agent = headers.get("User-Agent")
            else:
                # Case-insensitive search for User-Agent in dict
                for key in headers:
                    if key.lower() == "user-agent":
                        user_agent = headers[key]
                        break

        # See if we can fetch the resource
        try:
            robots_handler.can_fetch(resource, user_agent=user_agent)
        except Exception as e:
            raise e

        # Use the domain's context to get its client
        return context.client.get(resource, headers=headers)
