import pytest
from re import escape

from ethicrawl.core import Url
from ethicrawl.config import HttpProxyConfig


class TestHttpProxyConfig:
    def test_http_proxy_config_creation(self):
        url = "https://www.example.com"
        HttpProxyConfig(url, Url(url))
        HttpProxyConfig()
        with pytest.raises(
            ValueError, match=escape("Only File and HTTP(S) URLs supported: foo")
        ):
            HttpProxyConfig("foo")
        with pytest.raises(TypeError, match=escape("url must be Url, string, or None")):
            HttpProxyConfig(1)

    def test_getters(self):
        url = "https://www.example.com"
        hpc = HttpProxyConfig()
        hpc.http
        hpc.https
        hpc = HttpProxyConfig(url, Url(url))
        hpc.http
        hpc.https

    def test_setters(self):
        url = "https://www.example.com"
        hpc = HttpProxyConfig()
        hpc.http = None
        hpc.http = url
        hpc.http = Url(url)
        hpc.https = None
        hpc.https = url
        hpc.https = Url(url)
        with pytest.raises(TypeError, match="url must be Url, string, or None"):
            hpc.http = set()
        with pytest.raises(TypeError, match="url must be Url, string, or None"):
            hpc.https = set()

    def test_dict(self):
        assert isinstance(HttpProxyConfig().to_dict(), dict)
