from dataclasses import dataclass


from .context import Context
from ethicrawl.core import Resource
from ethicrawl.client import Client
from ethicrawl.functions import validate_resource

from ethicrawl.robots import Robot, RobotFactory
from ethicrawl.sitemaps import SitemapParser

from .synchronous_client import SynchronousClient


@dataclass
class TargetContext(Context):
    @validate_resource
    def __init__(self, resource: Resource, client: Client) -> None:
        super().__init__(resource=resource, client=SynchronousClient(client))
        self._robot = RobotFactory.robot(Context(resource=resource, client=client))

    @property
    def robot(self) -> Robot:
        return self._robot

    @property
    def sitemap(self) -> SitemapParser:
        if not hasattr(self, "_sitemap"):
            self._sitemap = SitemapParser(self)
        return self._sitemap
