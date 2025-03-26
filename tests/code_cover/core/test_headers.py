import pytest

from ethicrawl.core import Headers


class TestHeaders:
    def test_headers(self):
        headers = Headers()
        headers["User-Agent"] = "foo"
        headers["User-Agent"] = None
        headers["User-Agent"] = set()

        with pytest.raises(TypeError, match="Header keys must be strings, got int"):
            headers.__getitem__(1)

        with pytest.raises(TypeError, match="Header keys must be strings, got int"):
            headers[1] = None

        with pytest.raises(TypeError, match="Expected dict-like object, got set"):
            headers = Headers(set())

        headers = Headers({"User-Agent": "bar"})

        assert headers["User-Agent"] == "bar"

        headers = Headers(Baz="baz")

        assert headers["Baz"] == "baz"

        headers = Headers[{"a": "b"}]

    def test_headers_with_dict_like_object(self):
        """Test initialization with various dict-like objects."""

        # Create a simple dict-like class
        class DictLike:
            def __init__(self):
                self.data = {"Content-Type": "application/json"}

            def items(self):
                return self.data.items()

        # This should work now
        headers = Headers(DictLike())
        assert headers["content-type"] == "application/json"

        # And this should fail
        class NotDictLike:
            def __init__(self):
                self.data = {"key": "value"}

            # No items() method

        with pytest.raises(TypeError):
            Headers(NotDictLike())

    def test_headers_with_non_dict_like_objects(self):
        """Test that initializing with non-dict-like objects raises TypeError."""
        # Test with list (has no items() method)
        with pytest.raises(TypeError) as excinfo:
            Headers([1, 2, 3])
        assert "Expected dict-like object" in str(excinfo.value)

        # Test with integer
        with pytest.raises(TypeError) as excinfo:
            Headers(123)
        assert "Expected dict-like object" in str(excinfo.value)

        # Test with string (string has items() but it's not what we want)
        with pytest.raises(TypeError) as excinfo:
            Headers("not-a-dict")
        assert "Expected dict-like object" in str(excinfo.value)

    def test_getitem_with_non_string_key(self):
        """Test that __getitem__ raises TypeError for non-string keys."""
        headers = Headers({"Content-Type": "text/html"})

        with pytest.raises(TypeError) as excinfo:
            headers[123]
        assert "Header keys must be strings" in str(excinfo.value)

        with pytest.raises(TypeError) as excinfo:
            headers[None]
        assert "Header keys must be strings" in str(excinfo.value)

        with pytest.raises(TypeError) as excinfo:
            headers[("tuple", "key")]
        assert "Header keys must be strings" in str(excinfo.value)

    def test_contains_with_non_string_key(self):
        """Test that __contains__ returns False for non-string keys."""
        headers = Headers({"Content-Type": "text/html"})

        # These should all return False rather than raising exceptions
        assert 123 not in headers
        assert None not in headers
        assert (1, 2, 3) not in headers
        assert True not in headers

        # Make sure strings still work correctly
        assert "content-type" in headers
        assert "CONTENT-TYPE" in headers
        assert "not-a-header" not in headers

    def test_get_with_non_string_key(self):
        """Test that get() returns default value for non-string keys without raising exceptions."""
        headers = Headers({"Content-Type": "application/json", "X-Custom": "value"})

        # Test with different non-string key types
        assert headers.get(123) is None  # Integer key
        assert headers.get(None) is None  # None key
        assert headers.get(("tuple", "key")) is None  # Tuple key
        assert headers.get(True) is None  # Boolean key

        # Test with custom default value
        custom_default = "DEFAULT"
        assert headers.get(123, custom_default) == custom_default
        assert headers.get(None, custom_default) == custom_default

        # Verify this behavior is different from __getitem__
        # __getitem__ raises TypeError, while get() returns default
        with pytest.raises(TypeError):
            headers[123]  # This should raise TypeError

        # But get() doesn't raise
        assert headers.get(123) is None  # This should return None without error

        # Make sure get() still works correctly with string keys
        assert headers.get("content-type") == "application/json"  # Case-insensitive
        assert headers.get("X-CUSTOM") == "value"  # Case-insensitive
        assert headers.get("nonexistent") is None  # Missing key
        assert (
            headers.get("nonexistent", "custom-default") == "custom-default"
        )  # Missing with default
