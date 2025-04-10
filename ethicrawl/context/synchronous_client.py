from ethicrawl.core import Resource
from ethicrawl.client import Client, Response


class SynchronousClient(Client):
    def __init__(self, client: Client):
        self._client = client

    def get(self, resource: Resource, headers=None) -> Response:
        from ethicrawl.client.http import HttpClient

        if isinstance(self._client, HttpClient):
            return self._client.get(resource, headers=headers)
        return self._client.get(resource)
