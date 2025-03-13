import pytest
from ethicrawl.core.resource_list import ResourceList
from ethicrawl.core.resource import Resource


class TestResourceList:
    """Tests for the ResourceList class."""

    def test_resource_list_initialization(self):
        """Test creating ResourceList objects."""
        # Create empty list
        resources = ResourceList()
        assert len(resources) == 0

        # Create with initial items
        resources = ResourceList(
            [
                Resource("https://example.com/page1"),
                Resource("https://example.com/page2"),
            ]
        )
        assert len(resources) == 2

    def test_resource_list_operations(self):
        """Test list operations."""
        resources = ResourceList()

        # Append
        resources.append(Resource("https://example.com/page1"))
        assert len(resources) == 1

        # Extend
        resources.extend(
            [
                Resource("https://example.com/page2"),
                Resource("https://example.com/page3"),
            ]
        )
        assert len(resources) == 3

        # Indexing
        assert str(resources[0].url) == "https://example.com/page1"

        # Slicing
        slice = resources[1:3]
        assert len(slice) == 2
        assert str(slice[0].url) == "https://example.com/page2"

    def test_resource_list_filter(self):
        """Test filtering resource lists."""
        resources = ResourceList(
            [
                Resource("https://example.com/products/item1"),
                Resource("https://example.com/about"),
                Resource("https://example.com/products/item2"),
                Resource("https://example.com/contact"),
            ]
        )

        # Filter by pattern
        product_pages = resources.filter(r"/products/")
        assert len(product_pages) == 2

        # All items should match pattern
        for res in product_pages:
            assert "/products/" in str(res.url)

    def test_invalid_operations(self):
        """Test error handling for invalid operations."""
        resources = ResourceList()

        # Can't add non-Resource items
        with pytest.raises(TypeError):
            resources.append("https://example.com")
