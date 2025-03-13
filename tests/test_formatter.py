import pytest
import logging
from colorama import Fore, Style
from ethicrawl.logger.formatter import ColorFormatter


class TestColorFormatter:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a default formatter
        self.default_fmt = "%(levelname)s: %(message)s"
        self.formatter = ColorFormatter(self.default_fmt)

        # Create log records with different levels for testing
        self.debug_record = self.create_log_record(logging.DEBUG, "Debug message")
        self.info_record = self.create_log_record(logging.INFO, "Info message")
        self.warning_record = self.create_log_record(logging.WARNING, "Warning message")
        self.error_record = self.create_log_record(logging.ERROR, "Error message")
        self.critical_record = self.create_log_record(
            logging.CRITICAL, "Critical message"
        )

    def create_log_record(self, level, message):
        """Helper to create a log record."""
        record = logging.LogRecord(
            name="test",
            level=level,
            pathname=__file__,
            lineno=42,
            msg=message,
            args=(),
            exc_info=None,
        )
        return record

    def test_initialization(self):
        """Test initializing the formatter with different parameters."""
        # Test default initialization
        formatter = ColorFormatter()
        assert formatter.use_colors == True

        # Test with explicit format and no colors
        custom_fmt = "%(asctime)s [%(levelname)s] %(message)s"
        formatter = ColorFormatter(custom_fmt, use_colors=False)
        assert formatter.use_colors == False
        assert formatter._fmt == custom_fmt

    def test_format_with_colors(self):
        """Test formatting with colors enabled."""
        # Format a message
        formatted = self.formatter.format(self.info_record)

        # Check that the levelname has color codes around it
        expected_level_with_color = f"{Fore.GREEN}INFO{Style.RESET_ALL}"
        assert expected_level_with_color in formatted
        assert formatted.startswith(expected_level_with_color)
        assert formatted.endswith("Info message")

    def test_format_without_colors(self):
        """Test formatting with colors disabled."""
        # Create formatter with colors disabled
        no_color_formatter = ColorFormatter(self.default_fmt, use_colors=False)

        # Format a message
        formatted = no_color_formatter.format(self.info_record)

        # Check that no color codes are present
        assert Fore.GREEN not in formatted
        assert Style.RESET_ALL not in formatted
        assert formatted == "INFO: Info message"

    def test_all_log_levels(self):
        """Test that all log levels get the correct colors."""
        # Test each log level
        color_mappings = {
            "DEBUG": (self.debug_record, Fore.CYAN),
            "INFO": (self.info_record, Fore.GREEN),
            "WARNING": (self.warning_record, Fore.YELLOW),
            "ERROR": (self.error_record, Fore.RED),
            "CRITICAL": (self.critical_record, Fore.RED + Style.BRIGHT),
        }

        for level_name, (record, expected_color) in color_mappings.items():
            formatted = self.formatter.format(record)
            expected_colored_level = f"{expected_color}{level_name}{Style.RESET_ALL}"
            assert expected_colored_level in formatted

    def test_custom_format_string(self):
        """Test with a custom format string."""
        custom_fmt = "[%(levelname)s] %(name)s - %(message)s"
        formatter = ColorFormatter(custom_fmt)

        formatted = formatter.format(self.warning_record)
        expected_colored_level = f"{Fore.YELLOW}WARNING{Style.RESET_ALL}"

        assert formatted.startswith(f"[{expected_colored_level}]")
        assert "test - Warning message" in formatted
