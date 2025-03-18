import os
import tempfile

from ethicrawl.core import Resource
from ethicrawl.config import Config
from ethicrawl.logger import Logger


class TestLogger:

    def test_logger(self):
        # Get platform-appropriate temp directory
        temp_dir = tempfile.gettempdir()
        log_filename = "foo/ethicrawl_test.log"
        log_path = os.path.join(temp_dir, log_filename)
        log_dir = os.path.dirname(log_path)

        # Clean up any previous test file
        if os.path.exists(log_path):
            os.remove(log_path)

        url = "https://www.example.com"
        resource = Resource(url)
        Logger().setup_logging()
        Logger().reset()

        # Configure file logging with our temp path
        Config().logger.use_colors = False
        Config().logger.file_enabled = True
        Config().logger.file_path = log_path
        Logger().setup_logging()

        # Trigger some logging to ensure file creation
        test_message = "Test log message"
        logger = Logger().logger(resource, "test")
        logger.info(test_message)
        logger = Logger().logger(resource)

        # Force logger to flush its handlers
        import logging

        logging.shutdown()

        # Verify log file was created
        assert os.path.exists(log_path), f"Log file was not created at {log_path}"

        # Verify log file contains our message
        with open(log_path, "r") as f:
            log_content = f.read()
            assert (
                test_message in log_content
            ), f"Log file doesn't contain test message: {log_content}"

        # Clean up
        try:
            if os.path.exists(log_path):
                os.remove(log_path)
            if os.path.exists(log_dir) and os.path.basename(log_dir) == "foo":
                os.rmdir(log_dir)  # Only remove if empty and named "foo"
        except (OSError, PermissionError) as e:
            print(f"Warning: Could not remove temp files: {e}")
