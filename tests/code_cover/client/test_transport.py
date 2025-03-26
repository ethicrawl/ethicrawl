import pytest

from ethicrawl.client import Request, Response, Transport


class TestTransport(Transport):
    def test_transport(self):
        url = "https://www.example.com"
        request = Request(url)
        self.get(request)
        with pytest.raises(
            NotImplementedError, match="This transport does not support HEAD requests"
        ):
            self.head(request)
        self.user_agent = "foo"
        self.user_agent

    def get(self, request: Request) -> Response:
        return super().get(request)

    def head(self, request: Request) -> Response:
        return super().head(request)
