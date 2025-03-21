from abc import ABC, abstractmethod

from ethicrawl.client.response import Response


class Transport(ABC):
    """Abstract base class for HTTP transport implementations."""

    @abstractmethod
    def get(self, request) -> Response:
        """
        Make a GET request using the provided request object.

        Args:
            request (HttpRequest): The request to perform

        Returns:
            HttpResponse: The response from the server
        """

    def head(self, request) -> Response:
        """
        Make a HEAD request (optional implementation). TODO: have a look at this and other verbs if they make sense.
        """
        raise NotImplementedError(
            "This transport does not support HEAD requests")

    @property
    def user_agent(self) -> str:
        """
        Get the User-Agent string used by this transport.
        Default implementation returns a standard string.
        """
        return None

    @user_agent.setter
    def user_agent(self, agent):
        """
        Set the User-Agent string for this transport.
        Base implementation does nothing - concrete transports
        should implement this according to their needs.
        """
        pass  # Concrete transports should override this
