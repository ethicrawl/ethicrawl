from dataclasses import dataclass

from ethicrawl.core import Resource
from ethicrawl.client import Client
from ethicrawl.functions import validate_resource
from ethicrawl.robots import Robot, RobotFactory
from ethicrawl.sitemaps import SitemapParser

from .context import Context
from .synchronous_client import SynchronousClient


@dataclass
class TargetContext(Context):
    """Context for a specific target domain with synchronous operations.

    This class extends the base Context to provide domain-specific functionality
    including robots.txt handling and sitemap parsing capabilities. It ensures
    all operations use the synchronous client implementation.
    """

    @validate_resource
    def __init__(self, resource: Resource, client: Client) -> None:
        """Initialize a target context for a specific domain.

        Args:
            resource: The resource representing the target domain
            client: The client to use for HTTP requests
        """
        super().__init__(resource=resource, client=SynchronousClient(client))
        self._robot = RobotFactory.robot(Context(resource=resource, client=client))

    @property
    def robot(self) -> Robot:
        """Robot instance for accessing robots.txt functionality.

        Returns:
            Robot: The robot instance for this domain
        """
        return self._robot

    @property
    def sitemap(self) -> SitemapParser:
        """Sitemap parser for this domain.

        The sitemap parser is lazily initialized on first access.

        Returns:
            SitemapParser: The sitemap parser for this domain
        """
        if not hasattr(self, "_sitemap"):
            self._sitemap = SitemapParser(self)
        return self._sitemap
