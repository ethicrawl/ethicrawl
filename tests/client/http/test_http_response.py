import pytest

from ethicrawl.core import Headers
from ethicrawl.client.http import HttpResponse, HttpRequest


class TestHttpResponse:
    pass

    def test_creation(self):
        url = "https://www.example.com"
        HttpResponse(
            url=url,
            request=HttpRequest(url),
            content=bytes("foo", "utf8"),
            status_code=200,
            headers=Headers({}),
            text="bar",
        )

        with pytest.raises(
            ValueError,
            match="Invalid HTTP status code: 1. Must be between 100 and 599.",
        ):
            HttpResponse(
                url=url,
                request=HttpRequest(url),
                status_code=1,
            )

        with pytest.raises(
            ValueError,
            match="Invalid HTTP status code: 600. Must be between 100 and 599.",
        ):
            HttpResponse(
                url=url,
                request=HttpRequest(url),
                status_code=600,
            )

        with pytest.raises(
            TypeError,
            match="Expected int, got float",
        ):
            HttpResponse(
                url=url,
                request=HttpRequest(url),
                status_code=1.0,
            )

        with pytest.raises(
            TypeError,
            match="request must be an HttpRequest instance, got NoneType",
        ):
            HttpResponse(
                url=url,
                request=None,
                status_code=200,
            )

        with pytest.raises(TypeError, match="content must be bytes or None"):
            HttpResponse(
                url=url,
                request=HttpRequest(url),
                content="not-bytes",  # Wrong type
                status_code=200,
            )

        with pytest.raises(TypeError, match="text must be a string or None"):
            HttpResponse(
                url=url,
                request=HttpRequest(url),
                status_code=200,
                content=bytes("foo", "utf8"),
                text=1,  # Wrong type
            )

    def test_str(self):
        url = "https://www.example.com"
        HttpResponse(
            url=url,
            status_code=200,
            request=HttpRequest(url),
            text="foo",
        )
        headers = Headers()
        headers["Content-Type"] = "text/foo"
        text = ""
        for i in range(300):
            text += "ha"
        response = str(
            HttpResponse(
                url=url,
                status_code=200,
                request=HttpRequest(url),
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
                url=url,
                status_code=200,
                request=HttpRequest(url),
                headers=headers,
                content=bytes(text, "utf8"),
                text=text,
            )
        )
