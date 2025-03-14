import pytest
from ethicrawl.client.http_request import HttpRequest, Headers
from ethicrawl.core.url import Url
from ethicrawl.config import Config


class TestHeaders:
    def test_initialization_empty(self):
        """Test initializing an empty Headers object."""
        headers = Headers()
        assert len(headers) == 0
        assert isinstance(headers, dict)

    def test_initialization_with_dict(self):
        """Test initializing Headers with a dictionary."""
        initial = {"User-Agent": "Test/1.0", "Accept": "text/html"}
        headers = Headers(initial)

        assert len(headers) == 2
        assert headers["User-Agent"] == "Test/1.0"
        assert headers["Accept"] == "text/html"

    def test_none_value_removes_key(self):
        """Test that setting a value to None removes the key."""
        headers = Headers({"User-Agent": "Test/1.0", "Accept": "text/html"})

        # Set a value to None
        headers["Accept"] = None

        # Key should be removed
        assert "Accept" not in headers
        assert len(headers) == 1
        assert headers["User-Agent"] == "Test/1.0"

    def test_setting_normal_values(self):
        """Test setting normal values works as expected."""
        headers = Headers()

        # Add values
        headers["User-Agent"] = "Test/1.0"
        headers["Accept"] = "text/html"

        # Values should be set
        assert headers["User-Agent"] == "Test/1.0"
        assert headers["Accept"] == "text/html"

        # Update a value
        headers["User-Agent"] = "Updated/2.0"
        assert headers["User-Agent"] == "Updated/2.0"

    def test_remove_nonexistent_key(self):
        """Test setting a nonexistent key to None doesn't error."""
        headers = Headers()

        # This should not raise an error
        headers["Nonexistent"] = None

        # Header count should still be 0
        assert len(headers) == 0


class TestHttpRequest:
    def setup_method(self):
        """Set up test fixtures."""
        # Reset Config singleton to avoid test interference
        Config.reset()

        # Create a URL for testing
        self.url = Url("https://example.com/path")

    def test_initialization_with_defaults(self):
        """Test initializing HttpRequest with default values."""
        request = HttpRequest(self.url)

        # Check inheritance from Resource
        assert request.url == self.url

        # Check default values
        assert request.timeout == 30.0
        assert isinstance(request.headers, Headers)
        assert len(request.headers) == 0

    def test_initialization_with_custom_values(self):
        """Test initializing HttpRequest with custom values."""
        custom_headers = {"User-Agent": "CustomBot/1.0", "Accept": "application/json"}
        request = HttpRequest(self.url, _timeout=60.0, headers=custom_headers)

        # Check custom values
        assert request.timeout == 60.0
        assert isinstance(request.headers, Headers)
        assert request.headers["User-Agent"] == "CustomBot/1.0"
        assert request.headers["Accept"] == "application/json"

    def test_initialization_with_config_headers(self):
        """Test that headers from Config are added during initialization."""
        # Set some headers in the config
        config = Config()
        config.http.headers["X-Test"] = "ConfigValue"

        request = HttpRequest(self.url)

        # Headers from config should be added
        assert "X-Test" in request.headers
        assert request.headers["X-Test"] == "ConfigValue"

    def test_timeout_property(self):
        """Test the timeout property getter and setter."""
        request = HttpRequest(self.url)

        # Test setter with valid values
        request.timeout = 45.0
        assert request.timeout == 45.0

        # Test setter with integer (should be converted to float)
        request.timeout = 60
        assert request.timeout == 60.0
        assert isinstance(request.timeout, float)

    def test_timeout_validation(self):
        """Test timeout validation."""
        request = HttpRequest(self.url)

        # Test with invalid type
        with pytest.raises(TypeError, match="timeout must be a number"):
            request.timeout = "60"

        # Test with non-positive value
        with pytest.raises(ValueError, match="timeout must be positive"):
            request.timeout = 0

        with pytest.raises(ValueError, match="timeout must be positive"):
            request.timeout = -1

    def test_convert_dict_to_headers(self):
        """Test that regular dict gets converted to Headers."""
        # Initialize with a regular dict
        regular_dict = {"User-Agent": "Test/1.0"}
        request = HttpRequest(self.url, headers=regular_dict)

        # Headers should be converted to Headers class
        assert isinstance(request.headers, Headers)
        assert request.headers["User-Agent"] == "Test/1.0"

    def test_headers_behavior(self):
        """Test specialized Headers behavior through HttpRequest."""
        request = HttpRequest(self.url)

        # Add a header
        request.headers["Authorization"] = "Bearer token123"
        assert request.headers["Authorization"] == "Bearer token123"

        # Remove a header by setting to None
        request.headers["Authorization"] = None
        assert "Authorization" not in request.headers
