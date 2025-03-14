import pytest
from ethicrawl.config.http_config import HttpConfig


class TestHttpConfig:
    def test_initialization_with_defaults(self):
        """Test initialization with default values."""
        config = HttpConfig()

        # Check default values
        assert config.timeout == 30.0
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.rate_limit == 0.5
        assert config.jitter == 0.2
        assert config.user_agent == "Ethicrawl/1.0"
        assert isinstance(config.headers, dict)
        assert len(config.headers) == 0

    def test_initialization_with_custom_values(self):
        """Test initialization with custom values."""
        config = HttpConfig(
            _timeout=60.0,
            _max_retries=5,
            _retry_delay=2.0,
            _rate_limit=1.0,
            _jitter=0.5,
            _user_agent="Custom/1.0",
            headers={"Accept": "application/json"},
        )

        # Check custom values
        assert config.timeout == 60.0
        assert config.max_retries == 5
        assert config.retry_delay == 2.0
        assert config.rate_limit == 1.0
        assert config.jitter == 0.5
        assert config.user_agent == "Custom/1.0"
        assert config.headers == {"Accept": "application/json"}

    def test_invalid_initialization_values(self):
        """Test that invalid initialization values are caught by __post_init__."""
        # Negative timeout
        with pytest.raises(ValueError, match="timeout must be positive"):
            HttpConfig(_timeout=-1)

        # Non-integer max_retries
        with pytest.raises(TypeError, match="max_retries must be an integer"):
            HttpConfig(_max_retries="three")

        # Negative retry_delay
        with pytest.raises(ValueError, match="retry_delay cannot be negative"):
            HttpConfig(_retry_delay=-0.5)

        # Invalid jitter
        with pytest.raises(ValueError, match="jitter must be between 0 and 1"):
            HttpConfig(_jitter=1.5)

        # Empty user_agent
        with pytest.raises(ValueError, match="user_agent cannot be empty"):
            HttpConfig(_user_agent="   ")

    # Property tests

    def test_timeout_property(self):
        """Test timeout property getter and setter."""
        config = HttpConfig()

        # Test setter
        config.timeout = 45.0
        assert config.timeout == 45.0

        # Test int conversion to float
        config.timeout = 60
        assert config.timeout == 60.0
        assert isinstance(config.timeout, float)

        # Test invalid values
        with pytest.raises(TypeError, match="timeout must be a number"):
            config.timeout = "60"

        with pytest.raises(ValueError, match="timeout must be positive"):
            config.timeout = 0

    def test_max_retries_property(self):
        """Test max_retries property getter and setter."""
        config = HttpConfig()

        # Test setter
        config.max_retries = 10
        assert config.max_retries == 10

        # Test zero value (should be allowed)
        config.max_retries = 0
        assert config.max_retries == 0

        # Test invalid values
        with pytest.raises(TypeError, match="max_retries must be an integer"):
            config.max_retries = 2.5

        with pytest.raises(ValueError, match="max_retries cannot be negative"):
            config.max_retries = -1

    def test_retry_delay_property(self):
        """Test retry_delay property getter and setter."""
        config = HttpConfig()

        # Test setter
        config.retry_delay = 3.5
        assert config.retry_delay == 3.5

        # Test int conversion to float
        config.retry_delay = 4
        assert config.retry_delay == 4.0
        assert isinstance(config.retry_delay, float)

        # Test zero value (should be allowed)
        config.retry_delay = 0
        assert config.retry_delay == 0.0

        # Test invalid values
        with pytest.raises(TypeError, match="retry_delay must be a number"):
            config.retry_delay = "3"

        with pytest.raises(ValueError, match="retry_delay cannot be negative"):
            config.retry_delay = -0.1

    def test_rate_limit_property(self):
        """Test rate_limit property getter and setter."""
        config = HttpConfig()

        # Test setter
        config.rate_limit = 2.5
        assert config.rate_limit == 2.5

        # Test int conversion to float
        config.rate_limit = 3
        assert config.rate_limit == 3.0
        assert isinstance(config.rate_limit, float)

        # Test None value (unlimited)
        config.rate_limit = None
        assert config.rate_limit is None

        # Test invalid values
        with pytest.raises(TypeError, match="rate_limit must be a number or None"):
            config.rate_limit = "2"

        with pytest.raises(ValueError, match="rate_limit must be positive or None"):
            config.rate_limit = 0

    def test_jitter_property(self):
        """Test jitter property getter and setter."""
        config = HttpConfig()

        # Test setter
        config.jitter = 0.8
        assert config.jitter == 0.8

        # Test int conversion to float
        config.jitter = 0
        assert config.jitter == 0.0
        assert isinstance(config.jitter, float)

        # Test boundary values
        config.jitter = 0.0
        assert config.jitter == 0.0

        config.jitter = 0.999
        assert config.jitter == 0.999

        # Test invalid values
        with pytest.raises(TypeError, match="jitter must be a number"):
            config.jitter = "0.5"

        with pytest.raises(ValueError, match="jitter must be between 0 and 1"):
            config.jitter = -0.1

        with pytest.raises(ValueError, match="jitter must be between 0 and 1"):
            config.jitter = 1.0  # Equal to 1 should be invalid

    def test_user_agent_property(self):
        """Test user_agent property getter and setter."""
        config = HttpConfig()

        # Test setter
        config.user_agent = "Custom Bot/2.0"
        assert config.user_agent == "Custom Bot/2.0"

        # Test with whitespace (should be preserved)
        config.user_agent = "  Spaced Agent/1.0  "
        assert config.user_agent == "  Spaced Agent/1.0  "

        # Test invalid values
        with pytest.raises(TypeError, match="user_agent must be a string"):
            config.user_agent = 123

        with pytest.raises(ValueError, match="user_agent cannot be empty"):
            config.user_agent = ""

        with pytest.raises(ValueError, match="user_agent cannot be empty"):
            config.user_agent = "   "  # Whitespace only

    def test_headers_property(self):
        """Test headers dictionary behavior."""
        config = HttpConfig()

        # Initially empty
        assert len(config.headers) == 0

        # Add headers
        config.headers["User-Agent"] = "Custom/1.0"
        config.headers["Accept"] = "application/json"

        assert len(config.headers) == 2
        assert config.headers["User-Agent"] == "Custom/1.0"
        assert config.headers["Accept"] == "application/json"

        # Replace header
        config.headers["User-Agent"] = "Modified/2.0"
        assert config.headers["User-Agent"] == "Modified/2.0"

        # Remove header
        del config.headers["Accept"]
        assert "Accept" not in config.headers
        assert len(config.headers) == 1
