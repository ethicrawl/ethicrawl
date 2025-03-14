import pytest
import logging
from ethicrawl.config.logger_config import LoggerConfig


class TestLoggerConfig:
    def test_initialization_with_defaults(self):
        """Test initialization with default values."""
        config = LoggerConfig()

        # Check default values
        assert config.level == logging.INFO
        assert config.console_enabled is True
        assert config.file_enabled is False
        assert config.file_path is None
        assert config.use_colors is True
        assert config.component_levels == {}
        assert config.format == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def test_initialization_with_custom_values(self):
        """Test initialization with custom values."""
        config = LoggerConfig(
            _level=logging.DEBUG,
            _console_enabled=False,
            _file_enabled=True,
            _file_path="/tmp/log.txt",
            _use_colors=False,
            _format="%(levelname)s: %(message)s",
            _component_levels={"robots": logging.WARNING},
        )

        # Check custom values
        assert config.level == logging.DEBUG
        assert config.console_enabled is False
        assert config.file_enabled is True
        assert config.file_path == "/tmp/log.txt"
        assert config.use_colors is False
        assert config.format == "%(levelname)s: %(message)s"
        # Component levels should be initialized but not checked in post_init
        assert "robots" in config.component_levels
        assert config.component_levels["robots"] == logging.WARNING

    # Property tests

    def test_level_property(self):
        """Test level property with different input types."""
        config = LoggerConfig()

        # Test with integer values
        config.level = logging.DEBUG
        assert config.level == logging.DEBUG

        config.level = logging.WARNING
        assert config.level == logging.WARNING

        # Test with string values
        config.level = "DEBUG"
        assert config.level == logging.DEBUG

        config.level = "INFO"
        assert config.level == logging.INFO

        config.level = "warning"  # Should handle case insensitive
        assert config.level == logging.WARNING

        # Test invalid values
        with pytest.raises(ValueError, match="Unknown log level"):
            config.level = "TRACE"  # Not a Python log level

        with pytest.raises(
            TypeError, match="Log level must be an integer or level name string"
        ):
            config.level = 3.14  # Not an int or string

        with pytest.raises(
            TypeError, match="Log level must be an integer or level name string"
        ):
            config.level = True  # Not an int or string

    def test_console_enabled_property(self):
        """Test console_enabled property."""
        config = LoggerConfig()

        # Test valid values
        config.console_enabled = False
        assert config.console_enabled is False

        config.console_enabled = True
        assert config.console_enabled is True

        # Test invalid values
        with pytest.raises(TypeError, match="console_enabled must be a boolean"):
            config.console_enabled = "True"

        with pytest.raises(TypeError, match="console_enabled must be a boolean"):
            config.console_enabled = 1

    def test_file_enabled_property(self):
        """Test file_enabled property."""
        config = LoggerConfig()

        # Test valid values
        config.file_enabled = True
        assert config.file_enabled is True

        config.file_enabled = False
        assert config.file_enabled is False

        # Test invalid values
        with pytest.raises(TypeError, match="file_enabled must be a boolean"):
            config.file_enabled = "False"

        with pytest.raises(TypeError, match="file_enabled must be a boolean"):
            config.file_enabled = 0

    def test_file_path_property(self):
        """Test file_path property."""
        config = LoggerConfig()

        # Test valid values
        config.file_path = "/var/log/app.log"
        assert config.file_path == "/var/log/app.log"

        config.file_path = None
        assert config.file_path is None

        # Test invalid values
        with pytest.raises(TypeError, match="file_path must be a string or None"):
            config.file_path = 123

        with pytest.raises(TypeError, match="file_path must be a string or None"):
            config.file_path = True

    def test_use_colors_property(self):
        """Test use_colors property."""
        config = LoggerConfig()

        # Test valid values
        config.use_colors = False
        assert config.use_colors is False

        config.use_colors = True
        assert config.use_colors is True

        # Test invalid values
        with pytest.raises(TypeError, match="use_colors must be a boolean"):
            config.use_colors = "True"

        with pytest.raises(TypeError, match="use_colors must be a boolean"):
            config.use_colors = 1

    def test_format_property(self):
        """Test format property."""
        config = LoggerConfig()

        # Test valid values
        config.format = "%(levelname)s - %(message)s"
        assert config.format == "%(levelname)s - %(message)s"

        # Test invalid values
        with pytest.raises(TypeError, match="format must be a string"):
            config.format = 123

        with pytest.raises(ValueError, match="format string cannot be empty"):
            config.format = ""

    def test_component_levels_property(self):
        """Test component_levels property (read-only)."""
        config = LoggerConfig()

        # Initially empty
        assert config.component_levels == {}

        # Add component level
        config.set_component_level("http", logging.DEBUG)

        # Should see the added component level
        assert config.component_levels == {"http": logging.DEBUG}

        # Test that returned dict is a copy (can't modify original)
        levels = config.component_levels
        levels["sitemap"] = logging.WARNING

        # Original shouldn't be affected
        assert "sitemap" not in config.component_levels

    def test_set_component_level_with_int_level(self):
        """Test set_component_level with integer log levels."""
        config = LoggerConfig()

        # Set component levels with integer values
        config.set_component_level("http", logging.DEBUG)
        config.set_component_level("sitemap", logging.WARNING)

        # Check they were set correctly
        assert config.component_levels["http"] == logging.DEBUG
        assert config.component_levels["sitemap"] == logging.WARNING

    def test_set_component_level_with_string_level(self):
        """Test set_component_level with string log levels."""
        config = LoggerConfig()

        # Set component levels with string values
        config.set_component_level("http", "DEBUG")
        config.set_component_level("sitemap", "warning")  # Mixed case

        # Check they were converted correctly
        assert config.component_levels["http"] == logging.DEBUG
        assert config.component_levels["sitemap"] == logging.WARNING

    def test_set_component_level_with_invalid_level(self):
        """Test set_component_level with invalid log levels."""
        config = LoggerConfig()

        # Invalid string level
        with pytest.raises(ValueError, match="Unknown log level"):
            config.set_component_level("http", "TRACE")

        # Invalid type
        with pytest.raises(
            TypeError, match="Log level must be an integer or level name string"
        ):
            config.set_component_level("http", True)
