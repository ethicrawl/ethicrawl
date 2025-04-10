from ethicrawl.core import Resource
from ethicrawl.client import Client, Response


class SynchronousClient(Client):
    """Synchronous wrapper for client implementations.

    This class ensures that all client requests are made synchronously,
    providing a consistent interface regardless of the underlying client
    implementation. It delegates to the wrapped client while maintaining
    the synchronous operation contract.
    """

    def __init__(self, client: Client):
        """Initialize a synchronous client wrapper.

        Args:
            client: The client implementation to wrap
        """
        self._client = client

    def get(self, resource: Resource, headers=None) -> Response:
        """Synchronously fetch a resource.

        Makes a GET request to the specified resource using the underlying
        client implementation, but ensures the operation is synchronous.

        Args:
            resource: The resource to fetch
            headers: Optional headers for the request

        Returns:
            Response: The HTTP response from the resource
        """
        from ethicrawl.client.http import HttpClient

        if isinstance(self._client, HttpClient):
            return self._client.get(resource, headers=headers)
        return self._client.get(resource)
