import pytest


from ethicrawl.client import NoneClient
from ethicrawl.core import Resource, Url
from ethicrawl.context import Context, ContextManager
from ethicrawl.error import DomainWhitelistError


class TestContextManager:
    def test_context_manager(self):
        r = Resource(Url("https://www.example.com"))
        cm = ContextManager()

        # try to bind with a invalid client
        with pytest.raises(TypeError, match="Expected Client or None, got int"):
            cm.bind(r, 1)

        # set a binding manually to prevent it calling out to robots
        cm._contexts[r.url.base] = Context(r, NoneClient())
        # test unbinding a bound site
        assert cm.unbind(r) == True
        # test unbinding an unbound site
        with pytest.raises(ValueError, match="https://www.example.com is not bound"):
            cm.unbind(r)

        # set a binding manually to prevent it calling out to robots
        # cm._contexts[r.url.base] = Context(r, NoneClient())

        # check robots, sitemaps and client fail on unbound sites
        with pytest.raises(
            DomainWhitelistError,
            match="Cannot access URL 'https://www.example.com' - domain not whitelisted.",
        ):
            cm.robot(r)

        with pytest.raises(
            DomainWhitelistError,
            match="Cannot access URL 'https://www.example.com' - domain not whitelisted.",
        ):
            cm.sitemap(r)
