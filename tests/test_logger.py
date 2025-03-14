import os
import logging
import pytest
from unittest.mock import patch, MagicMock
import tempfile

from ethicrawl.logger.logger import Logger
from ethicrawl.config import Config
from ethicrawl.core.resource import Resource
from ethicrawl.core.url import Url


class TestLogger:
    def setup_method(self):
        """Set up test fixtures."""
        # Reset logger before each test
        Logger.reset()
        # Reset config for consistent test results
        Config.reset()

    def teardown_method(self):
        """Clean up after each test."""
        Logger.reset()
        Config.reset()

    def test_file_logging_setup(self):
        """Test that file logging is set up correctly."""
        # Create a temporary directory for the log file
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = os.path.join(temp_dir, "test.log")

            # Configure file logging
            config = Config()
            config.logger.file_enabled = True
            config.logger.file_path = log_path
            config.logger.level = logging.DEBUG

            # Initialize logging
            Logger.setup_logging()

            # Verify file handler was created
            assert Logger._file_handler is not None
            assert isinstance(Logger._file_handler, logging.FileHandler)
            assert Logger._file_handler.baseFilename == log_path

            # Create a logger and log something
            resource = Resource(Url("https://example.com"))
            logger = Logger.logger(resource, "test")
            logger.debug("Test debug message")
            logger.info("Test info message")

            # Close the handler to ensure all logs are written
            Logger._file_handler.close()

            # Verify the log file was created and contains our messages
            with open(log_path, "r") as f:
                log_content = f.read()
                assert "Test debug message" in log_content
                assert "Test info message" in log_content

    def test_file_logging_directory_creation(self):
        """Test that log directories are created if they don't exist."""
        # Create a temporary directory for the base path
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a path with a subdirectory that doesn't exist
            log_dir = os.path.join(temp_dir, "logs", "nested")
            log_path = os.path.join(log_dir, "test.log")

            # Verify the directory doesn't exist yet
            assert not os.path.exists(log_dir)

            # Configure file logging
            config = Config()
            config.logger.file_enabled = True
            config.logger.file_path = log_path

            # Initialize logging
            Logger.setup_logging()

            # Verify directory was created
            assert os.path.exists(log_dir)

            # Verify file handler was created
            assert Logger._file_handler is not None
            assert Logger._file_handler.baseFilename == log_path

    def test_reset(self):
        """Test that reset() properly resets logger state."""
        # First set up logging with some configuration
        config = Config()
        config.logger.console_enabled = True

        # Initialize logging
        Logger.setup_logging()

        # Verify it's initialized
        assert Logger._initialized is True
        assert Logger._console_handler is not None

        # Get the original root logger handlers count
        root_logger = logging.getLogger()
        original_handlers_count = len(root_logger.handlers)
        assert original_handlers_count > 0

        # Reset logging
        Logger.reset()

        # Verify reset worked
        assert Logger._initialized is False
        assert Logger._console_handler is None
        assert Logger._file_handler is None

        # Verify root logger handlers were removed
        assert len(root_logger.handlers) == 0
