import pytest

from ethicrawl.config import HttpConfig, HttpProxyConfig


class TestHttpConfig:
    def test_timeout(self):
        hc = HttpConfig()
        with pytest.raises(TypeError, match="timeout must be a number"):
            hc.timeout = None
        with pytest.raises(ValueError, match="timeout must be positive"):
            hc.timeout = -1
        with pytest.raises(ValueError, match="maximum timeout is 300 seconds"):
            hc.timeout = 9999999
        hc.timeout = 30.5
        assert hc.timeout == 30.5

    def test_retries(self):
        hc = HttpConfig()
        with pytest.raises(TypeError, match="max_retries must be an integer"):
            hc.max_retries = 0.1
        with pytest.raises(ValueError, match="max_retries cannot be negative"):
            hc.max_retries = -1
        with pytest.raises(ValueError, match="max_retries cannot be more than 10"):
            hc.max_retries = 9999999
        hc.max_retries = 10
        assert hc.max_retries == 10
        with pytest.raises(TypeError, match="retry_delay must be a number"):
            hc.retry_delay = None
        with pytest.raises(ValueError, match="retry_delay cannot be negative"):
            hc.retry_delay = -1
        with pytest.raises(ValueError, match="retry_delay cannot be more than 60"):
            hc.retry_delay = 9999999
        hc.retry_delay = 10
        assert hc.retry_delay == 10

    def test_rate_limit(self):
        hc = HttpConfig()
        with pytest.raises(TypeError, match="rate_limit must be a number"):
            hc.rate_limit = "foo"
        with pytest.raises(ValueError, match="rate_limit must be positive"):
            hc.rate_limit = -1
        hc.rate_limit = 10
        assert hc.rate_limit == 10

    def test_jitter(self):
        hc = HttpConfig()
        with pytest.raises(TypeError, match="jitter must be a number"):
            hc.jitter = "foo"
        with pytest.raises(ValueError, match="jitter must be between 0 and 1"):
            hc.jitter = -0.1
        with pytest.raises(ValueError, match="jitter must be between 0 and 1"):
            hc.jitter = 1.1
        hc.jitter = 0.5
        assert hc.jitter == 0.5

    def test_user_agent(self):
        hc = HttpConfig()
        with pytest.raises(TypeError, match="user_agent must be a string"):
            hc.user_agent = set()
        with pytest.raises(ValueError, match="user_agent cannot be empty"):
            hc.user_agent = ""
        hc.user_agent = "Foo Bar Baz"
        assert hc.user_agent == "Foo Bar Baz"

    def test_headers(self):
        hc = HttpConfig()
        with pytest.raises(TypeError, match="Headers must be a dictionary"):
            hc.headers = set()
        with pytest.raises(
            TypeError, match="Header value must be a string, got <class 'int'>"
        ):
            hc.headers = {"foo": "bar", "baz": 1}
        with pytest.raises(
            TypeError, match="Header key must be a string, got <class 'int'>"
        ):
            hc.headers = {"foo": "bar", 1: "baz"}
        hc.headers = {"foo": "bar", "baz": "foo"}
        assert hc.headers == {"foo": "bar", "baz": "foo"}

    def test_proxies(self):
        hc = HttpConfig()
        hcp = HttpProxyConfig()
        hc.proxies = hcp
        assert hc.proxies is hcp
        hc.proxies = hcp.to_dict()
        with pytest.raises(
            TypeError, match="proxies must be a HttpProxyConfig instance or dictionary"
        ):
            hc.proxies = 1
