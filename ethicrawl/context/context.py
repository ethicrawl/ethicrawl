# FIXME: remove comment, imports sorted

from typing import Any, Optional

from ethicrawl.client import Client, NoneClient
from ethicrawl.core import Resource
from ethicrawl.logger import Logger


class Context:
    def __init__(self, resource: Resource, client: Optional[Client] = None) -> None:
        self._resource = self._validate_resource(resource)
        self._client = self._validate_client(client)
        self._logger = Logger.logger(self._resource, "core")

    def _validate_client(self, client: Any) -> Client:  # Use Any for runtime
        """Validate client is either None or a Client instance."""
        if client is None:
            client = NoneClient()
        if not isinstance(client, Client):
            raise TypeError(
                f"client must be a Client instance or None, got {type(client)}"
            )
        return client

    def _validate_resource(self, resource: Any) -> Resource:
        """Validate resource is a Resource instance."""
        if not isinstance(resource, Resource):
            raise TypeError(
                f"resource must be a Resource instance, got {type(resource)}"
            )
        return resource

    @property
    def resource(self) -> Resource:
        return self._resource

    @resource.setter
    def resource(self, resource: Resource):
        self._resource = self._validate_resource(resource)

    @property
    def client(self) -> Client:
        return self._client

    @client.setter
    def client(self, client: Optional[Client]):
        self._client = self._validate_client(client)

    def logger(self, component: str):
        """Get a component-specific logger within this context."""
        return Logger.logger(self._resource, component)

    def __str__(self) -> str:
        """Return a human-readable string representation of the context."""
        return f"EthicrawlContext({self._resource.url})"

    def __repr__(self) -> str:
        """Return an unambiguous string representation of the context."""
        return (
            f"EthicrawlContext(url='{self._resource.url}', client={repr(self._client)})"
        )
