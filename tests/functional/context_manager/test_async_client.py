import pytest

from ethicrawl.context.asynchronous_client import AsynchronousClient
from ethicrawl.core import Resource, Url


class TestAsynchronousClient:

    def test_async_client(self):
        r = Resource(Url("https://www.example.com/"))
        a = AsynchronousClient()

        with pytest.raises(NotImplementedError):
            a.get(r)
