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
            with pytest.raises(
                TypeError, match=f"Expected list got {type(junk).__name__}"
            ):
                ResourceList(junk)

    def test_invalid_resource_list_initialisation(self):
        with pytest.raises(
            TypeError,
            match=f"Expected Resource, got int",
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

    def test_slice_behavior(self):
        """Test that slicing a ResourceList returns a new ResourceList with the sliced items."""
        # Create a ResourceList with multiple items
        r1 = Resource("https://www.example.com/one")
        r2 = Resource("https://www.example.com/two")
        r3 = Resource("https://www.example.com/three")
        r4 = Resource("https://www.example.com/four")
        r5 = Resource("https://www.example.com/five")
        rl = ResourceList([r1, r2, r3, r4, r5])

        # Test basic slicing returns a ResourceList
        slice_result = rl[1:4]
        assert isinstance(slice_result, ResourceList)
        assert len(slice_result) == 3
        assert slice_result[0] == r2
        assert slice_result[1] == r3
        assert slice_result[2] == r4

        # Test slice to end
        end_slice = rl[3:]
        assert isinstance(end_slice, ResourceList)
        assert len(end_slice) == 2
        assert end_slice[0] == r4
        assert end_slice[1] == r5

        # Test slice from start
        start_slice = rl[:2]
        assert isinstance(start_slice, ResourceList)
        assert len(start_slice) == 2
        assert start_slice[0] == r1
        assert start_slice[1] == r2

        # Test empty slice
        empty_slice = rl[5:10]
        assert isinstance(empty_slice, ResourceList)
        assert len(empty_slice) == 0

        # Test step slicing
        step_slice = rl[::2]  # Every other item
        assert isinstance(step_slice, ResourceList)
        assert len(step_slice) == 3
        assert step_slice[0] == r1
        assert step_slice[1] == r3
        assert step_slice[2] == r5

        # Test negative indexing in slice
        neg_slice = rl[-3:-1]
        assert isinstance(neg_slice, ResourceList)
        assert len(neg_slice) == 2
        assert neg_slice[0] == r3
        assert neg_slice[1] == r4

        # Make sure original list is unchanged
        assert len(rl) == 5
        assert rl[0] == r1
        assert rl[4] == r5
