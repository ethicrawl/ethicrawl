import pytest
import logging

from ethicrawl.context import Context
from ethicrawl.core import Resource
from ethicrawl.client import Client, NoneClient


class TestContext:
    def test_initialize_without_client(self):
        r = Resource("https://www.example.com")
        c = Context(r)
        assert isinstance(c.client, Client)
        assert c.resource == r

    def test_initialize_with_client(self):
        nc = NoneClient()
        r = Resource("https://www.example.com")
        c = Context(r, nc)
        assert isinstance(c.client, NoneClient)
        assert c.client == nc
        assert c.client != NoneClient()

    def test_initialize_with_junk(self):
        with pytest.raises(
            TypeError,
            match=f"resource must be a Resource instance, got int",
        ):
            c = Context(1)
        r = Resource("https://www.example.com")
        with pytest.raises(
            TypeError,
            match=f"client must be a Client instance or None, got int",
        ):
            c = Context(r, 1)

    def test_resource_setter(self):
        r = Resource("https://www.example.com")
        c = Context(r)
        c.resource = r
        with pytest.raises(
            TypeError,
            match=f"resource must be a Resource instance, got int",
        ):
            c.resource = 1

    def test_client_setter(self):
        r = Resource("https://www.example.com")
        c = Context(r)
        c.client = NoneClient()
        with pytest.raises(
            TypeError,
            match=f"client must be a Client instance or None, got int",
        ):
            c.client = 1

    def test_logger(self):
        r = Resource("https://www.example.com")
        c = Context(r)
        assert isinstance(c.logger("foo"), logging.Logger)

    def test_str(self):
        u = "https://www.example.com"
        r = Resource(u)
        c = Context(r)
        assert str(c) == f"EthicrawlContext({u})"

    def test_repr(self):
        u = "https://www.example.com"
        r = Resource(u)
        c = Context(r)
        repr_str = repr(c)
        assert f"url='{u}'" in repr_str
        assert "client=" in repr_str
