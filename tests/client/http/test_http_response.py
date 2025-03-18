import pytest

from ethicrawl.core import Headers
from ethicrawl.client.http import HttpResponse, HttpRequest


class TestHttpResponse:
    pass

    def test_creation(self):
        url = "https://www.example.com"
        HttpResponse(url, 200, HttpRequest(url), {}, bytes("foo", "utf8"), "bar")
        with pytest.raises(
            ValueError,
            match="Invalid HTTP status code: 1. Must be between 100 and 599.",
        ):
            HttpResponse(url, 1, HttpRequest(url))
        with pytest.raises(
            ValueError,
            match="Invalid HTTP status code: 600. Must be between 100 and 599.",
        ):
            HttpResponse(url, 600, HttpRequest(url))
        with pytest.raises(
            TypeError,
            match="status_code must be an integer",
        ):
            HttpResponse(url, 1.0, HttpRequest(url))
        with pytest.raises(
            TypeError,
            match="request must be an HttpRequest instance, got NoneType",
        ):
            HttpResponse(url, 200, None)
        with pytest.raises(TypeError, match="content must be bytes or None"):
            HttpResponse(url, 200, HttpRequest(url), {}, 1, "bar")
        with pytest.raises(TypeError, match="text must be a string or None"):
            HttpResponse(url, 200, HttpRequest(url), {}, bytes("foo", "utf8"), 1)

    def test_str(self):
        url = "https://www.example.com"
        HttpResponse(url, 200, HttpRequest(url), text="foo")
        headers = Headers()
        headers["Content-Type"] = "text/foo"
        text = ""
        for i in range(300):
            text += "ha"
        response = str(
            HttpResponse(
                url,
                200,
                HttpRequest(url),
                headers=headers,
                content=bytes(text, "utf8"),
                text=text,
            )
        )
        assert "HTTP 200" in response
        assert "URL: https://www.example.com" in response
        headers["Content-Type"] = "image/foo"
        response = str(
            HttpResponse(
                url,
                200,
                HttpRequest(url),
                headers=headers,
                content=bytes(text, "utf8"),
                text=text,
            )
        )
