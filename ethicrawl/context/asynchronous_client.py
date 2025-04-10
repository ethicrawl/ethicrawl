from ethicrawl.client import Client, Response
from ethicrawl.core import Resource


class AsynchronousClient(Client):
    """Asynchronous implementation of the Client interface.

    This client provides non-blocking HTTP request capabilities for
    making requests to web resources. It implements the standard Client
    interface but uses asynchronous I/O operations.
    """

    def get(self, resource: Resource) -> Response:
        """Asynchronously fetch a resource.

        Args:
            resource: The resource to fetch

        Returns:
            Response: The HTTP response from the resource

        Raises:
            NotImplementedError: This method is not yet implemented
        """
        raise NotImplementedError
