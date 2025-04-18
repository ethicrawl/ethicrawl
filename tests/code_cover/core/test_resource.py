import pytest
import re

from ethicrawl.core import Resource, Url


class TestResource:
    def test_resource_initialisation_with_string(self):
        url = "https://www.example.com"
        assert Resource(url).url == url

    def test_resource_initialisation_with_url(self):
        url = "https://www.example.com"
        assert Resource(Url(url)).url == url

    def test_resource_initialisation_with_junk(self):
        with pytest.raises(
            TypeError,
            match=re.escape(f"Error creating resource, got int expected str or Url"),
        ):
            Resource(1).url

    def test_resource_hashable(self):
        url = "https://www.example.com"
        set({Resource(url)})

    def test_resource_equality(self):
        url = "https://www.example.com"
        assert Resource(url) == Resource(url)
        assert Resource(url) != 1

    def test_resource_str_and_repr(self):
        url = "https://www.example.com"
        assert str(Resource(url)) == url
        assert repr(Resource(url)) == f"Resource('{url}')"
