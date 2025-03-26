from ethicrawl.core import Resource
from ethicrawl.client import Client, NoneClient


class TestClient(Client):
    def test_client(self):
        self.get(Resource("https://www.example.com/"))
        nc = NoneClient()
        nc.get(Resource("https://www.example.com/"))

    def get(self, resource: Resource):
        return super().get(resource)
