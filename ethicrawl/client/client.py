from abc import ABC, abstractmethod
from typing import Optional

from ethicrawl.core import Resource, Headers

from .response import Response
from .request import Request


class Client(ABC):
    """Abstract base class defining the interface for all clients.

    This defines the contract that any client implementation must follow,
    whether it's an HTTP client, file client, or other protocol. The Client
    abstraction enables dependency injection throughout the system and allows
    for easy swapping of implementations for different protocols or testing.

    All client implementations must provide at least the get() method to
    fetch resources. Specific implementations may add additional methods
    or parameters as needed.
    """

    @abstractmethod
    def get(
        self,
        resource: Resource,
    ) -> Response:
        """Fetch a resource.

        Retrieves the content associated with the provided resource.

        Args:
            resource: The Resource to fetch

        Returns:
            A Response object containing the result

        Raises:
            Various exceptions depending on the implementation
        """
        pass


class NoneClient(Client):
    """Null object implementation of Client that returns empty responses.

    This implementation serves as a placeholder when no client is needed
    or available. It follows the Null Object pattern to avoid null checks
    throughout the codebase. The NoneClient always returns empty responses
    without actually making any network requests.

    This class is useful for:
    - Providing a default when no client is specified
    - Testing components that need a Client but shouldn't make real requests
    - Stubbing functionality during development
    """

    def get(self, resource: Resource) -> Response:
        """Return an empty response without doing any work.

        Args:
            resource: The resource that would be requested (unused)

        Returns:
            An empty Response object with the same URL
        """
        return Response(resource.url, Request(resource.url))
