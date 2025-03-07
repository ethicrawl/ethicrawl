import urllib.parse
import socket

from ethicrawl.core.ethicrawl_context import EthicrawlContext as Context
from ethicrawl.robots.robots_handler import RobotsHandler
from ethicrawl.client.http_client import HttpClient
from ethicrawl.core.url import Url
from ethicrawl.config.config import Config
import logging

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

    def bind(self, url: Url, client: HttpClient = None):
        url = Url(str(url), validate=True)
        client = client or HttpClient()
        self._context = Context(url, client)
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
    def sitemaps(self):
        if not hasattr(self, "_sitemap_index") and not isinstance():
            pass

    def get(self, url: str):
        pass
        # try:
        #     parsed_url = self._parse_url(url)

        #     # Check domain permissions
        #     domain = parsed_url.netloc
        #     if domain not in self._allowed_domains:
        #         raise ValueError(f"Domain not allowed: {domain}")

        #     # Get the appropriate client for this domain
        #     client = self._allowed_domains[domain]

        #     # Check robots.txt rules only for the main site domain
        #     if domain == self._base_domain:
        #         if not self._robots_.can_fetch(parsed_url.geturl()):
        #             raise ValueError(
        #                 f"URL disallowed by robots.txt: {parsed_url.geturl()}"
        #             )

        #     # Finally, fetch the response with the domain-specific client
        #     return client.get(parsed_url.geturl())
        # except ValueError as e:
        #     raise
