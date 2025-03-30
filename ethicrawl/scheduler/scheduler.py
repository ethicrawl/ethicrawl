from functools import wraps

from ethicrawl.context import Context
from ethicrawl.core import Headers, Resource, ResourceList, Url
from ethicrawl.context import Context
from ethicrawl.client import Client, NoneClient, Response
from ethicrawl.client.http import HttpClient
from ethicrawl.error import RobotDisallowedError, DomainWhitelistError
from ethicrawl.robots import RobotFactory, Robot
from ethicrawl.sitemaps import SitemapParser


def validate_resource(func):
    """Decorator that validates the first argument is a Resource instance."""

    @wraps(func)
    def wrapper(self, resource, *args, **kwargs):
        if not isinstance(resource, Resource):
            raise TypeError(f"Expected Resource, got {type(resource).__name__}")
        return func(self, resource, *args, **kwargs)

    return wrapper


class ScheduledClient(Client):
    def __init__(self, scheduler: "Scheduler"):
        self._scheduler = scheduler

    def get(self, resource: Resource, headers=None) -> Response:
        """Route requests through scheduler for concurrency management."""
        print(f"routing {resource.url} via the scheduler")
        return self._scheduler.get(resource, headers)


class TargetContext(Context):
    @validate_resource
    def __init__(self, resource: Resource, client: Client) -> None:
        super().__init__(resource=resource, client=ScheduledClient(client))
        self._robot = RobotFactory.robot(Context(resource=resource, client=client))

    @property
    def robot(self) -> Robot:
        return self._robot


class Scheduler:
    def __init__(self):
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
            if isinstance(target_context.client, HttpClient):
                if not target_context.robot.can_fetch(resource, user_agent=user_agent):
                    raise RobotDisallowedError(str(resource.url), user_agent)
                self._logger.debug("Request permitted by robots.txt policy")
                return target_context.client.get(resource, headers=headers)
            else:
                return target_context.client.get(resource)
        else:
            raise DomainWhitelistError(resource.url)

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
            return SitemapParser(self._contexts[resource.url.base])
        else:
            raise DomainWhitelistError(resource.url)
