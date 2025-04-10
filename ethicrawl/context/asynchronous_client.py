from ethicrawl.client import Client, Response
from ethicrawl.core import Resource


class AsynchronousClient(Client):

    def get(self, resource: Resource) -> Response:
        raise NotImplementedError
