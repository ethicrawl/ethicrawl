import pytest
from ethicrawl.core.resource import Resource
from ethicrawl.core.url import Url


class TestResource:
    """Tests for the Resource class."""

    def test_resource_initialization(self):
        """Test creating Resource objects."""
        # Create with a URL object
        url = Url("https://example.com/page")
        resource = Resource(url)
        assert str(resource.url) == "https://example.com/page"

        # Create with a string URL
        resource = Resource("https://example.com/page")
        assert str(resource.url) == "https://example.com/page"
        assert isinstance(resource.url, Url)

    def test_resource_equality(self):
        """Test resource equality."""
        res1 = Resource("https://example.com/page")
        res2 = Resource("https://example.com/page")
        res3 = Resource("https://example.com/other")

        assert res1 == res2
        assert res1 != res3

        # Different types should not be equal
        assert res1 != "https://example.com/page"

    def test_resource_hashable(self):
        """Test that resources can be used in sets/dicts."""
        resources = {
            Resource("https://example.com/page1"),
            Resource("https://example.com/page2"),
            Resource("https://example.com/page1"),  # Duplicate
        }

        # Set should deduplicate
        assert len(resources) == 2

    def test_invalid_resource(self):
        """Test error handling for invalid resources."""
        with pytest.raises(ValueError):
            Resource(123)  # Not a string or URL
