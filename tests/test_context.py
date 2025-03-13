import pytest
from ethicrawl.core.context import Context
from ethicrawl.core.resource import Resource
from unittest.mock import MagicMock


class TestContext:
    def test_context_initialization(self):
        """Test context creation with just a resource."""
        resource = Resource("https://example.com")
        context = Context(resource)

        assert context.resource == resource
        assert context.client is None

    def test_context_with_http_client(self):
        """Test context creation with a resource and HTTP client."""
        resource = Resource("https://example.com")

        # Create a mock HttpClient
        mock_client = MagicMock()
        mock_client.__class__.__name__ = "HttpClient"
        # Make isinstance() return True for this mock when checking if it's an HttpClient
        mock_client.__class__.__module__ = "ethicrawl.client.http_client"

        # Patch the isinstance check to pass our mock
        from unittest.mock import patch

        with patch("ethicrawl.core.context.isinstance", return_value=True):
            context = Context(resource, mock_client)

            assert context.resource == resource
            assert context.client == mock_client

    def test_context_properties(self):
        """Test context properties."""
        resource = Resource("https://example.com")
        context = Context(resource)

        # Test resource getter/setter
        new_resource = Resource("https://example.org")
        context.resource = new_resource
        assert context.resource == new_resource

        # Test client setter with None
        context.client = None
        assert context.client is None

    def test_context_logger(self):
        """Test the logger method."""
        resource = Resource("https://example.com")
        context = Context(resource)

        # Get a component logger
        logger = context.logger("test-component")
        assert logger is not None

    def test_context_string_representations(self):
        """Test string representations of Context."""
        resource = Resource("https://example.com")
        context = Context(resource)

        # Test __str__ and __repr__
        str_repr = str(context)
        assert "EthicrawlContext" in str_repr
        assert "https://example.com" in str_repr

        repr_str = repr(context)
        assert "EthicrawlContext" in repr_str
        assert "https://example.com" in repr_str
