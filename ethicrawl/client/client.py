from abc import ABC, abstractmethod

from ethicrawl.core import Resource

from .response import Response
from .request import Request


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


class NoneClient(Client):
    def get(self, resource: Resource) -> Response:
        return Response(resource.url, Request(resource.url))
