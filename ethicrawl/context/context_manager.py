from ethicrawl.core import Headers, Resource
from ethicrawl.client import Client, NoneClient, Response
from ethicrawl.error import RobotDisallowedError, DomainWhitelistError
from ethicrawl.robots import Robot
from ethicrawl.sitemaps import SitemapParser
from ethicrawl.functions import validate_resource

from .synchronous_client import SynchronousClient
from .target_context import TargetContext


class ContextManager:
    def __init__(self) -> None:
        self._default_client = NoneClient()
        self._contexts: dict[str, TargetContext] = {}

    @validate_resource
    def bind(
        self,
        resource: Resource,
        client: Client | None = None,
    ) -> bool:
        if isinstance(client, (Client | None)):
            client = client or self._default_client
            target_context = TargetContext(
                resource=resource,
                client=client,
            )
            self._contexts[resource.url.base] = target_context
            if not hasattr(self, "_logger"):
                self._logger = target_context.logger("scheduler")
        else:
            raise TypeError(f"Expected Client or None, got {type(client).__name__}")
        return True

    @validate_resource
    def unbind(
        self,
        resource: Resource,
    ) -> bool:
        if resource.url.base in self._contexts:
            del self._contexts[resource.url.base]
        else:
            raise ValueError(f"{resource.url.base} is not bound")
        return True

    @validate_resource
    def get(
        self,
        resource: Resource,
        headers: Headers | None = None,
    ) -> Response:
        user_agent = None
        if headers:
            headers = Headers(headers)
            user_agent = headers.get("User-Agent")
        if resource.url.base in self._contexts:
            target_context: TargetContext = self._contexts[resource.url.base]
            if isinstance(target_context.client, (SynchronousClient)):
                if not target_context.robot.can_fetch(resource, user_agent=user_agent):
                    raise RobotDisallowedError(str(resource.url), user_agent)
                self._logger.debug("Request permitted by robots.txt policy")
                return target_context.client.get(resource, headers=headers)
            else:
                return target_context.client.get(resource)
        else:
            raise DomainWhitelistError(resource.url)

    @validate_resource
    def client(self, resource: Resource) -> Client | None:
        if resource.url.base in self._contexts:
            return (self._contexts[resource.url.base]).client
        return None

    @validate_resource
    def robot(self, resource: Resource) -> Robot:
        """Get the robot instance for a resource's domain.

        Args:
            resource: The resource to get the robot for

        Returns:
            Robot: The robot instance for this domain

        Raises:
            DomainWhitelistError: If the domain is not registered
        """
        if resource.url.base in self._contexts:
            return self._contexts[resource.url.base].robot
        else:
            raise DomainWhitelistError(resource.url)

    @validate_resource
    def sitemap(self, resource: Resource) -> SitemapParser:
        if resource.url.base in self._contexts:
            return self._contexts[resource.url.base].sitemap
        else:
            raise DomainWhitelistError(resource.url)
