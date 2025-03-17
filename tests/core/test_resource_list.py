import pytest

from ethicrawl.core import Resource, ResourceList


class TestResourceList:

    def test_empty_resource_list_initialisation(self):
        ResourceList()

    def test_non_empty_resource_list_initialisation(self):
        r = Resource("https://www.example.com")
        ResourceList([r, r])

    def test_wrong_type_resource_list_initialisation(self):
        invalid = [
            (1),
            (1, 2, 3),
            1,
            1.0,
            "a",
        ]
        for junk in invalid:
            with pytest.raises(TypeError, match=f"Expected list got {type(junk)}"):
                ResourceList(junk)

    def test_invalid_resource_list_initialisation(self):
        with pytest.raises(
            TypeError,
            match=f"Only Resource objects can be added, got <class 'int'>",
        ):
            ResourceList([Resource("https://www.example.com"), 1])

    def test_dunder_methods(self):
        r = Resource("https://www.example.com")
        rl = ResourceList([r, r])
        for i in rl:
            assert i.url == "https://www.example.com"
        assert rl[-1] == r
        assert len(rl) == 2
        rl = ResourceList()
        assert str(rl) == "[]"
        assert repr(rl) == "ResourceList([])"

    def test_to_list(self):
        r = Resource("https://www.example.com")
        rl = ResourceList([r, r])
        l = rl.to_list()
        assert len(l) == 2

    def test_string_filter(self):
        r1 = Resource("https://www.example.com/foo")
        r2 = Resource("https://www.example.com/bar")
        r3 = Resource("https://www.example.com/baz")
        rl = ResourceList([r1, r2, r3])
        assert len(rl.filter("foo")) == 1

    def test_regex_filter(self):
        r1 = Resource("https://www.example.com/foo")
        r2 = Resource("https://www.example.com/bar")
        r3 = Resource("https://www.example.com/baz")
        rl = ResourceList([r1, r2, r3])
        assert len(rl.filter(r"ba[r|z]")) == 2
