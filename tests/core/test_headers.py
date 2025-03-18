import pytest

from ethicrawl.core import Headers


class TestHeaders:
    def test_headers(self):
        headers = Headers()
        headers["User-Agent"] = "foo"
        headers["User-Agent"] = None
        headers["User-Agent"] = set()

        with pytest.raises(TypeError, match="Header keys must be strings, got int"):
            headers[1] = None

        headers = Headers({"User-Agent": "bar"})

        assert headers["User-Agent"] == "bar"

        headers = Headers(Baz="baz")

        assert headers["Baz"] == "baz"
