import urllib.parse
import socket

from typing import Union
from ethicrawl.core.context import Context
from ethicrawl.robots.robots_handler import RobotsHandler
from ethicrawl.client.http_client import HttpClient
from ethicrawl.core.url import Url
from ethicrawl.core.resource import Resource
from ethicrawl.config.config import Config
from ethicrawl.sitemaps.sitemaps import Sitemaps
import logging
from ethicrawl.client.http_response import HttpResponse

from functools import wraps


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

    def __init__(self):
        pass

    def for_dev_use_only_context(self) -> Context:
        """
        Get the internal context (advanced usage).

        Note: Most operations should be performed through Ethicrawl methods directly.
        Only use this for advanced customization or direct component access.

        This is here currently to support test development in the usage.py file and
        will be removed

        """
        if hasattr(self, "_context"):
            return self._context
        else:
            return None

    def bind(self, url: Union[str, Url], client: HttpClient = None):
        if isinstance(url, Resource):
            url = url.url
        url = Url(str(url), validate=True)
        resource = Resource(url)
        client = client or HttpClient()
        self._context = Context(resource, client)
        return True if self._context is not None else False

    def unbind(self):
        """
        Unbind from the current site and clear all cached resources.

        Returns:
            bool: True if successfully unbound
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
        if isinstance(url, Resource):
            url = url.url
        url = Url(str(url), validate=True)

        if not hasattr(self, "_whitelist"):
            self._whitelist = {}

        domain = url.netloc
        context = Context(Resource(url), client or self._context.client)
        try:
            robots_handler = RobotsHandler(context)
        except Exception as e:
            self.logger.warning(f"Failed to load robots.txt for {domain}: {e}")
            # Still create a permissive handler or use None
            robots_handler = None  # Or a permissive fallback

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

    @config.setter
    def config(self, config: Config):
        Config.update(config.to_dict())

    @property
    @ensure_bound
    def logger(self) -> logging.Logger:
        if not hasattr(self, "_logger"):
            self._logger = self._context.logger("")
        return self._logger

    @property
    @ensure_bound
    def robots(self) -> RobotsHandler:
        # lazy load robots
        if not hasattr(self, "_robots"):
            self._robots = RobotsHandler(self._context)
        return self._robots

    @property
    @ensure_bound
    def sitemaps(self) -> Sitemaps:
        if not hasattr(self, "_sitemaps"):
            self._sitemaps = Sitemaps(self._context)
        return self._sitemaps

    @ensure_bound
    def get(self, url: Union[str, Url, Resource]) -> HttpResponse:
        """
        Make an HTTP GET request to the specified URL, respecting robots.txt rules
        and domain whitelisting.

        Args:
            url: URL to fetch (string, Url object, or Resource object)

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
            raise TypeError(f"Expected string, Url, or Resource, got {type(url)}")

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

        # Check robots.txt rules if we have a handler
        if robots_handler:
            is_allowed = robots_handler.can_fetch(resource)
            if not is_allowed:
                # This is already logged as WARNING in the robots handler,
                raise ValueError(f"URL disallowed by robots.txt: {resource.url}")

        # Use the domain's context to get its client
        return context.client.get(resource)
