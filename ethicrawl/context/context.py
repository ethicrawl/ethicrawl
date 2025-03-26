from typing import Any

from ethicrawl.client import Client, NoneClient
from ethicrawl.core import Resource
from ethicrawl.logger import Logger


class Context:
    """Dependency container for crawler operations providing resource and client access.

    Context serves as a dependency injection mechanism that bundles a resource (URL)
    with a client for making requests. It provides type validation for these dependencies
    and simplifies passing related objects throughout the system.

    The class enables components to operate with a consistent set of dependencies
    without having to pass multiple parameters or manage connections independently.

    Attributes:
        resource: The Resource object representing the current target
        client: The Client used to make requests

    Example:
        >>> from ethicrawl.core import Resource
        >>> from ethicrawl.client.http import HttpClient
        >>> context = Context(Resource("https://example.com"), HttpClient())
        >>> response = context.client.get(context.resource)
        >>> logger = context.logger("robots")
        >>> logger.info("Processing robots.txt")
    """

    def __init__(self, resource: Resource, client: Client | None = None) -> None:
        """Initialize a Context with a resource and optional client.

        Args:
            resource: The Resource object representing the current URL
            client: Optional Client to use for requests. If None, a NoneClient
                will be used as a placeholder.

        Raises:
            TypeError: If resource is not a Resource instance
            TypeError: If client is not a Client instance or None
        """
        self._resource = self._validate_resource(resource)
        self._client = self._validate_client(client)
        self._logger = Logger.logger(self._resource, "core")

    def _validate_client(self, client: Client | None = None) -> Client:
        """Validate client is either None or a Client instance.

        Args:
            client: The client to validate

        Returns:
            A Client instance (creates NoneClient if input was None)

        Raises:
            TypeError: If client is not None and not a Client instance
        """
        if client is None:
            client = NoneClient()
        if not isinstance(client, Client):
            raise TypeError(
                f"client must be a Client instance or None, got {type(client).__name__}"
            )
        return client

    def _validate_resource(self, resource: Resource) -> Resource:
        """Validate resource is a Resource instance.

        Args:
            resource: The resource to validate

        Returns:
            The validated Resource object

        Raises:
            TypeError: If resource is not a Resource instance
        """
        if not isinstance(resource, Resource):
            raise TypeError(
                f"resource must be a Resource instance, got {type(resource).__name__}"
            )
        return resource

    @property
    def resource(self) -> Resource:
        """Get the current resource.

        Returns:
            The Resource object for this context
        """
        return self._resource

    @resource.setter
    def resource(self, resource: Resource):
        """Set the resource for this context.

        Args:
            resource: New Resource object

        Raises:
            TypeError: If resource is not a Resource instance
        """
        self._resource = self._validate_resource(resource)

    @property
    def client(self) -> Client:
        """Get the current client.

        Returns:
            The Client object for this context
        """
        return self._client

    @client.setter
    def client(self, client: Client | None):
        """Set the client for this context.

        Args:
            client: New Client object or None

        Raises:
            TypeError: If client is not None and not a Client instance
        """
        self._client = self._validate_client(client)

    def logger(self, component: str):
        """Get a component-specific logger within this context.

        Creates a logger associated with the current resource and
        the specified component name.

        Args:
            component: Component name for the logger

        Returns:
            A Logger instance for the specified component
        """
        return Logger.logger(self._resource, component)

    def __str__(self) -> str:
        """Return a human-readable string representation of the context."""
        return f"EthicrawlContext({self._resource.url})"

    def __repr__(self) -> str:
        """Return an unambiguous string representation of the context."""
        return (
            f"EthicrawlContext(url='{self._resource.url}', client={repr(self._client)})"
        )
