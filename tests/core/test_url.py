import pytest
import re

from ethicrawl.core import Url


class TestUrl:

    def test_url_initialisation(self):
        for url in [
            "http://www.example.com",
            "https://www.example.com/with/path",
            "file://tmp/foo",
        ]:
            assert isinstance(Url(url), Url)
            assert url == str(Url(url))

    def test_url_initialisation_with_url(self):
        url = Url(Url("https://www.example.com"))
        assert str(url) == "https://www.example.com"

    def test_url_initialisation_with_unsupported_protocol(self):
        url = "gopher://gopher.example.com"
        with pytest.raises(
            ValueError,
            match=re.escape(f"Only File and HTTP(S) URLs supported: {url}"),
        ):
            Url(url)

    def test_url_initialisation_http_with_missing_domain(self):
        url = "https:///foo"
        with pytest.raises(ValueError):
            Url(url)

    def test_url_initialisation_file_with_missing_path(self):
        url = "file://foo"
        with pytest.raises(ValueError):
            Url(url)

    def test_url_initialisation_with_valid_domain(self):
        url = Url("http://localhost", validate=True)
        assert str(url) == "http://localhost"

    def test_url_initialisation_with_invalid_domain(self):
        domain = "x"
        with pytest.raises(ValueError, match=f"Cannot resolve hostname: {domain}"):
            Url(f"http://{domain}", validate=True)

    def test_property_base(self):
        urls = {
            "http://www.example.com": "http://www.example.com",
            "file:///foo/bar": "file://",
        }
        for url, result in urls.items():
            assert Url(url).base == result

    def test_http_only_property(self):
        u = Url("file:///foo")
        assert u.scheme == "file"
        with pytest.raises(ValueError, match="Only valid for HTTP and HTTPS urls"):
            u.netloc

    def test_properties(self):
        u = Url("https://www.example.com:443/foo/bar;baz?q=v#1")
        assert u.scheme == "https"
        assert u.netloc == "www.example.com:443"
        assert u.hostname == "www.example.com"
        assert u.path == "/foo/bar"
        assert u.params == "baz"
        assert u.query == "q=v"
        assert u.query_params == {"q": "v"}
        assert u.fragment == "1"

    def test_equality(self):
        url = "https://www.example.com"
        a = Url(url)
        b = Url(url)
        assert a == b
        assert a == url
        assert a != None

    def test_hash(self):
        url = "https://www.example.com"
        set({Url(url)})

    # 3. Add single query parameter: extend("param_name", "param_value")

    def test_extend_path(self):
        url = "https://www.example.com"
        assert Url(url).extend("baz") == url + "/baz"
        url = "https://www.example.com/"
        assert Url(url).extend("baz") == url + "baz"
        url = "https://www.example.com/foo/bar"
        assert Url(url).extend("baz") == url + "/baz"
        url = "https://www.example.com/foo/bar/"
        assert Url(url).extend("baz") == url + "baz"
        url = "https://www.example.com/foo/bar"
        assert Url(url).extend("/baz") == url + "/baz"
        url = "https://www.example.com/foo/bar/"
        assert Url(url).extend("/baz") == url + "baz"

    def test_extend_query_dictionary(self):
        url = "https://www.example.com/"
        assert Url(url).extend({"q": "v"}) == url + "?q=v"
        url = "https://www.example.com"
        assert Url(url).extend({"q": "v"}) == url + "?q=v"
        url = "https://www.example.com/?a=b"
        assert Url(url).extend({"q": "v"}) == url + "&q=v"

    def test_extend_query_tuple(self):
        url = "https://www.example.com/"
        assert Url(url).extend("q", "v") == url + "?q=v"
        url = "https://www.example.com"
        assert Url(url).extend("q", "v") == url + "?q=v"
        url = "https://www.example.com/?a=b"
        assert Url(url).extend("q", "v") == url + "&q=v"

    def test_extend_with_params_preserves_url_components(self):
        # Test with semicolon parameters
        url = "https://www.example.com/path;param=value"
        assert (
            Url(url).extend({"q": "v"})
            == "https://www.example.com/path;param=value?q=v"
        )

        # Test with fragments
        url = "https://www.example.com/path#section"
        assert Url(url).extend({"q": "v"}) == "https://www.example.com/path?q=v#section"

        # Test with both semicolon parameters and fragments
        url = "https://www.example.com/path;param=value#section"
        assert (
            Url(url).extend({"q": "v"})
            == "https://www.example.com/path;param=value?q=v#section"
        )

        # Test with existing query parameters, semicolon params and fragments
        url = "https://www.example.com/path;param=value?a=b#section"
        assert (
            Url(url).extend({"q": "v"})
            == "https://www.example.com/path;param=value?a=b&q=v#section"
        )

    def test_extend_file(self):
        path = "file:///foo"
        assert Url(path).extend("bar") == path + "/bar"
        path = "file:///foo/"
        assert Url(path).extend("bar") == path + "bar"
        path = "file:///foo"
        assert Url(path).extend("/bar") == path + "/bar"
        path = "file:///foo/"
        assert Url(path).extend("/bar") == path + "bar"
        with pytest.raises(
            ValueError, match=f"Query parameters are not supported for file:// URLs"
        ):
            Url(path).extend("a", "b")
        with pytest.raises(
            ValueError, match=f"Query parameters are not supported for file:// URLs"
        ):
            Url(path).extend({"a": "b"})

    def test_extend_invalid(self):
        url = Url("https://www.example.com/")
        invalid = [
            (1),
            (1, 2, 3),
            1,
            1.0,
            {
                "a",
                "b",
                "c",
            },
        ]
        for param in invalid:
            with pytest.raises(ValueError, match=f"Invalid arguments for extend()"):
                url.extend(param)
