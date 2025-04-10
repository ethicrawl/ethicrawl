from ethicrawl.core import Headers, Resource
from ethicrawl.client import Client, NoneClient, Response
from ethicrawl.error import RobotDisallowedError, DomainWhitelistError
from ethicrawl.robots import Robot
from ethicrawl.sitemaps import SitemapParser
from ethicrawl.functions import validate_resource

from .synchronous_client import SynchronousClient
from .target_context import TargetContext


class ContextManager:
    """Manages target contexts for different domain resources.

    This class handles the lifecycle of domain contexts, including binding resources
    to clients, managing robots.txt permissions, and providing access to domain-specific
    functionality like robots.txt handlers and sitemaps.
    """

    def __init__(self) -> None:
        self._default_client = NoneClient()
        self._contexts: dict[str, TargetContext] = {}

    @validate_resource
    def bind(
        self,
        resource: Resource,
        client: Client | None = None,
    ) -> bool:
        """Bind a resource to a client in this context manager.

        Args:
            resource: The resource to bind
            client: The client to use for requests to this resource.
                   If None, uses the default client.

        Returns:
            bool: True if binding was successful

        Raises:
            TypeError: If client is not a Client instance or None
        """
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
        """Unbind a resource from this context manager.

        Args:
            resource: The resource to unbind

        Returns:
            bool: True if unbinding was successful

        Raises:
            ValueError: If the resource's domain is not bound
        """
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
        """Fetch a resource respecting robots.txt rules.

        Args:
            resource: The resource to fetch
            headers: Optional headers for the request

        Returns:
            Response: The HTTP response from the resource

        Raises:
            RobotDisallowedError: If the request is disallowed by robots.txt
            DomainWhitelistError: If the domain is not bound to this context manager
        """
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
        """Get the client for a resource's domain.

        Args:
            resource: The resource to get the client for

        Returns:
            Client: The client instance for this domain, or None if not found
        """
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
        """Get the sitemap parser for a resource's domain.

        Args:
            resource: The resource to get the sitemap parser for

        Returns:
            SitemapParser: The sitemap parser for this domain

        Raises:
            DomainWhitelistError: If the domain is not registered
        """
        if resource.url.base in self._contexts:
            return self._contexts[resource.url.base].sitemap
        else:
            raise DomainWhitelistError(resource.url)
