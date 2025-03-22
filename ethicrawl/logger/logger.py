# import logging

from logging import WARNING, FileHandler, Formatter
from logging import Logger as LoggingLogger
from logging import StreamHandler, getLogger
from os import makedirs, path
from re import sub
from sys import stdout

from ethicrawl.config import Config
from ethicrawl.core import Resource

from .formatter import ColorFormatter


class Logger:
    """Factory class for creating and retrieving loggers for Ethicrawl instances."""

    # Keep track of whether logging has been initialized
    _initialized = False

    # Cache for handlers to avoid duplicate creation
    _console_handler = None
    _file_handler = None

    @staticmethod
    def setup_logging() -> None:
        """
        Set up logging based on current configuration.
        This should be called once at application startup.
        """
        if Logger._initialized:
            return

        config = Config()
        log_config = config.logger

        # Configure root logger
        root_logger = getLogger()
        root_logger.setLevel(WARNING)  # Default level for non-app loggers

        # Remove existing handlers to avoid duplicates on re-initialization
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Create formatters
        console_formatter: Formatter
        if log_config.use_colors:
            console_formatter = ColorFormatter(log_config.format)
        else:
            console_formatter = Formatter(log_config.format)

        file_formatter = Formatter(log_config.format)

        # Set up console logging if enabled
        if log_config.console_enabled:
            console = StreamHandler(stdout)
            console.setFormatter(console_formatter)
            root_logger.addHandler(console)
            Logger._console_handler = console

        # Set up file logging if enabled
        if log_config.file_enabled and log_config.file_path:
            # Ensure directory exists
            log_dir = path.dirname(log_config.file_path)
            if log_dir and not path.exists(log_dir):
                makedirs(log_dir)

            file_handler = FileHandler(log_config.file_path)
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
            Logger._file_handler = file_handler

        # Configure the main application logger
        app_logger = getLogger(__name__.split(".")[0])  # 'ethicrawl'
        app_logger.setLevel(log_config.level)
        app_logger.propagate = True

        # Apply component-specific log levels
        for component, level in log_config.component_levels.items():
            component_logger = getLogger(f"{__name__.split('.')[0]}.*.{component}")
            component_logger.setLevel(level)

        Logger._initialized = True

    @staticmethod
    def _clean_name(name: str) -> str:
        """Clean a string to make it suitable as a logger name."""
        # Replace invalid characters with underscores
        name = sub(r"[^a-zA-Z0-9_\-\.]", "_", name)
        # Replace consecutive dots with a single dot
        name = sub(r"\.{2,}", ".", name)
        # Replace consecutive underscores with a single underscore
        name = sub(r"\_{2,}", "_", name)
        # Remove leading and trailing dots
        name = sub(r"^\.|\.$", "", name)
        return name or "unnamed"

    @staticmethod
    def logger(resource: Resource, component: str | None = None) -> LoggingLogger:
        """
        Get a logger for the specified URL, optionally with a component name.

        Args:
            url: The URL to create a logger for
            component: Optional component name (e.g., "robots", "sitemaps")

        Returns:
            A logger instance
        """

        if not Logger._initialized:
            Logger.setup_logging()

        prefix = __name__.split(".")[0]

        base = resource.url.base.replace(".", "_")

        # Build the logger name
        if component:
            logger_name = f"{prefix}.{base}.{component}"
        else:
            logger_name = f"{prefix}.{base}"

        # Clean the name for logger compatibility
        logger_name = Logger._clean_name(logger_name)

        # Get or create the logger
        logger = getLogger(logger_name)

        # Apply component-specific log level if applicable
        config = Config()
        if component and component in config.logger.component_levels:
            logger.setLevel(config.logger.component_levels[component])

        return logger

    @staticmethod
    def reset() -> None:
        """Reset logging configuration - useful for testing."""
        Logger._initialized = False
        Logger._console_handler = None
        Logger._file_handler = None

        # Reset the root logger
        root = getLogger()
        for handler in root.handlers[:]:
            root.removeHandler(handler)
