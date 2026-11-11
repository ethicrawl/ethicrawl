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


def _robots_client(robots_body: str = "User-agent: *\nDisallow: /private/\n"):
    """A mock Client whose robots.txt fetch returns ``robots_body``."""
    from unittest.mock import Mock

    from ethicrawl.client import Client

    client = Mock(spec=Client)
    robots_response = Mock()
    robots_response.status_code = 200
    robots_response.text = robots_body
    client.get.return_value = robots_response
    return client


class TestContextManagerGet:
    def test_get_enforces_robots_policy(self):
        from ethicrawl.error import RobotDisallowedError

        site = Resource(Url("https://www.example.com"))
        client = _robots_client()
        cm = ContextManager()
        cm.bind(site, client)

        allowed = Resource(Url("https://www.example.com/public/page"))
        assert cm.get(allowed) is client.get.return_value

        with pytest.raises(RobotDisallowedError):
            cm.get(Resource(Url("https://www.example.com/private/page")))

    def test_get_with_unwrapped_client_skips_robots(self):
        # Contexts normally wrap their client in a SynchronousClient; anything
        # else is passed straight through without a robots.txt check.
        site = Resource(Url("https://www.example.com"))
        client = _robots_client()
        cm = ContextManager()
        cm.bind(site, client)
        cm._contexts[site.url.base].client = client

        disallowed = Resource(Url("https://www.example.com/private/page"))
        assert cm.get(disallowed) is client.get.return_value
        client.get.assert_called_with(disallowed)

    def test_get_unbound_domain(self):
        cm = ContextManager()
        with pytest.raises(DomainWhitelistError):
            cm.get(Resource(Url("https://www.example.com/page")))

    def test_client_lookup(self):
        site = Resource(Url("https://www.example.com"))
        client = _robots_client()
        cm = ContextManager()

        assert cm.client(site) is None

        cm.bind(site, client)
        assert cm.client(site) is not None

    def test_methods_reject_non_resource(self):
        cm = ContextManager()
        with pytest.raises(TypeError, match="Expected Resource, got str"):
            cm.client("https://www.example.com")

    def test_get_raises_when_robot_returns_false(self):
        # Robot.can_fetch normally raises on its own; the manager still guards
        # against a robot that merely reports False.
        from unittest.mock import patch

        from ethicrawl.error import RobotDisallowedError

        site = Resource(Url("https://www.example.com"))
        cm = ContextManager()
        cm.bind(site, _robots_client())
        robot = cm._contexts[site.url.base].robot

        with patch.object(robot, "can_fetch", return_value=False):
            with pytest.raises(RobotDisallowedError):
                cm.get(Resource(Url("https://www.example.com/page")))
