import pytest

from ethicrawl.config import Config
from ethicrawl.core import Headers
from ethicrawl.client.http import HttpRequest


class TestHttpRequest:
    def test_create_http_request_timeout(self):
        url = "https://www.example.com"
        hr = HttpRequest(url)
        hr.timeout
        hr.timeout = 0.1
        with pytest.raises(ValueError, match="maximum timeout is 300 seconds"):
            hr.timeout = 999
        with pytest.raises(ValueError, match="timeout must be positive"):
            hr.timeout = -1
        with pytest.raises(TypeError, match="timeout must be a number"):
            hr.timeout = "foo"

    def test_create_headers(self):
        url = "https://www.example.com"

        # Save original headers
        original_headers = Config().http.headers.copy()

        try:
            # Clear existing headers and set a test one
            Config().http.headers.clear()
            Config().http.headers["User-Agent"] = "foo"

            # Verify config headers are set correctly
            assert (
                "User-Agent".lower() in Config().http.headers
            ), "Header not set in Config"

            # Create request
            hr = HttpRequest(url)

            # Debug values - uncomment if needed
            # print(f"Config headers: {dict(Config().http.headers)}")
            # print(f"Request headers: {dict(hr.headers)}")

            assert (
                "User-Agent".lower() in hr.headers
            ), "User-Agent not copied from Config"
            assert hr.headers["User-Agent"] == "foo"

            # Test custom headers override
            headers = Headers({"User-Agent": "bar"})
            hr = HttpRequest(url, headers=headers)
            assert hr.headers["User-Agent"] == "bar"

        finally:
            # Restore original headers
            Config().http.headers.clear()
            for k, v in original_headers.items():
                Config().http.headers[k] = v

    def test_create_with_dict(self):
        url = "https://www.example.com"
        hr = HttpRequest(url, headers={"User-Agent": "foo"})
        assert hr.headers["User-Agent"] == "foo"
