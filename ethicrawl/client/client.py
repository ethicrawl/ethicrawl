from abc import ABC, abstractmethod

from ethicrawl.core.resource import Resource
from ethicrawl.client.response import Response


class Client(ABC):
    """
    Abstract base class defining the interface for all clients.

    This defines the contract that any client implementation must follow,
    whether it's an HTTP client, file client, or other protocol.
    """

    @abstractmethod
    def get(
        self,
        resource: Resource,
    ) -> Response:
        """Fetch a resource."""
        pass


class NoneClient(Client):
    def get(self, resource: Resource) -> Response:
        return Response()
