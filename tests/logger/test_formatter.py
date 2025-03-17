import logging
import pytest
from colorama import Fore, Style
from io import StringIO

from ethicrawl.logger.formatter import ColorFormatter


class TestColorFormatter:

    @pytest.fixture
    def log_stream(self):
        """Create a StringIO object to capture log output."""
        return StringIO()

    @pytest.fixture
    def logger(self, log_stream):
        """Create a logger with a stream handler."""
        logger = logging.getLogger("test_formatter")
        logger.setLevel(logging.DEBUG)

        # Remove any existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Add a stream handler that writes to our StringIO
        handler = logging.StreamHandler(log_stream)
        logger.addHandler(handler)
        return logger, handler

    def test_color_formatting(self, logger, log_stream):
        """Test that colors are correctly applied to log levels."""
        logger_obj, handler = logger

        # Set our color formatter
        formatter = ColorFormatter("%(levelname)s: %(message)s", use_colors=True)
        handler.setFormatter(formatter)

        # Log messages at different levels
        logger_obj.debug("Debug message")
        logger_obj.info("Info message")
        logger_obj.warning("Warning message")
        logger_obj.error("Error message")
        logger_obj.critical("Critical message")

        # Get the logged output
        output = log_stream.getvalue()

        # Verify each level has its color
        assert Fore.CYAN + "DEBUG" + Style.RESET_ALL in output
        assert Fore.GREEN + "INFO" + Style.RESET_ALL in output
        assert Fore.YELLOW + "WARNING" + Style.RESET_ALL in output
        assert Fore.RED + "ERROR" + Style.RESET_ALL in output
        assert Fore.RED + Style.BRIGHT + "CRITICAL" + Style.RESET_ALL in output

    def test_no_colors(self, logger, log_stream):
        """Test that colors are not applied when use_colors=False."""
        logger_obj, handler = logger

        # Set formatter with colors disabled
        formatter = ColorFormatter("%(levelname)s: %(message)s", use_colors=False)
        handler.setFormatter(formatter)

        # Log a message
        logger_obj.info("Test message")

        # Get the logged output
        output = log_stream.getvalue()

        # Verify no color codes are present
        assert Fore.GREEN not in output
        assert Style.RESET_ALL not in output
        assert "INFO: Test message" in output

    def test_custom_format(self, logger, log_stream):
        """Test that custom format strings work correctly with colors."""
        logger_obj, handler = logger

        # Set a custom format
        custom_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        formatter = ColorFormatter(custom_format, use_colors=True)
        handler.setFormatter(formatter)

        # Log a message
        logger_obj.warning("Custom format test")

        # Get the logged output
        output = log_stream.getvalue()

        # Verify the color is applied only to the level name
        assert Fore.YELLOW + "WARNING" + Style.RESET_ALL in output
        assert "test_formatter: Custom format test" in output

    def test_format_preserves_message(self, logger, log_stream):
        """Test that the original message content is preserved."""
        logger_obj, handler = logger

        # Set our color formatter
        formatter = ColorFormatter("%(levelname)s: %(message)s", use_colors=True)
        handler.setFormatter(formatter)

        # Log a message with special characters
        special_msg = "Test with [brackets], {braces}, and special chars: !@#$%^&*()"
        logger_obj.info(special_msg)

        # Get the logged output
        output = log_stream.getvalue()

        # Verify the message content is preserved
        assert special_msg in output
