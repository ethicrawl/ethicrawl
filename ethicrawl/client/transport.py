from abc import ABC, abstractmethod

from ethicrawl.client.response import Response


class Transport(ABC):
    """Abstract base class for HTTP transport implementations.

    Transport defines the interface for making HTTP requests through various
    backends. Concrete implementations handle the actual request logic using
    different libraries or mechanisms (e.g., requests, selenium, etc.).

    This abstraction allows swapping transport mechanisms without changing
    the client interface, supporting different use cases such as basic HTTP
    requests or full browser automation.
    """

    @abstractmethod
    def get(self, request) -> Response:
        """Make a GET request using the provided request object.

        Args:
            request: The request to perform

        Returns:
            Response object containing the result

        Raises:
            NotImplementedError: If not implemented by subclass
        """

    def head(self, request) -> Response:
        """Make a HEAD request.

        Default implementation raises NotImplementedError.
        See GitHub issue #18 for planned implementation of HEAD and other HTTP verbs.

        Args:
            request: The request to perform

        Returns:
            Response object containing headers and status

        Raises:
            NotImplementedError: Default implementation raises this exception
        """
        raise NotImplementedError("This transport does not support HEAD requests")

    @property
    def user_agent(self) -> str:
        """Get the User-Agent string used by this transport.

        Returns:
            The current User-Agent string
        """
        return str(None)

    @user_agent.setter
    def user_agent(self, agent: str):
        """Set the User-Agent string for this transport.

        Base implementation does nothing. Concrete transports
        should implement this according to their capabilities.

        Args:
            agent: User agent string to set
        """
        return None
