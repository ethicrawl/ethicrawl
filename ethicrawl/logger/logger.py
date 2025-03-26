# import logging

from logging import WARNING, FileHandler, Formatter
from logging import Logger as LoggingLogger
from logging import StreamHandler, getLogger
from os import makedirs, path
from re import sub
from sys import stdout

from ethicrawl.config import Config
from ethicrawl.core import Resource

from .color_formatter import ColorFormatter


class Logger:
    """Factory class for creating and managing loggers throughout Ethicrawl.

    This class provides a centralized way to create and configure loggers based on
    the application's configuration settings. It supports:

    - Resource-specific loggers with hierarchical naming
    - Component-specific log levels
    - Console output with optional color formatting
    - File output with configurable paths
    - Initialization management to prevent duplicate configuration

    The Logger class is designed as a static utility class rather than being instantiated.
    All methods are static and operate on the global logging configuration.

    Example:
        >>> from ethicrawl.logger import Logger
        >>> from ethicrawl.core import Resource, Url
        >>> # Setup logging (happens automatically when first logger is created)
        >>> Logger.setup_logging()
        >>> # Get a logger for a specific resource
        >>> resource = Resource(Url("https://example.com"))
        >>> logger = Logger.logger(resource, "http")
        >>> logger.info("Making request to %s", resource.url)
    """

    # Keep track of whether logging has been initialized
    _initialized = False

    # Cache for handlers to avoid duplicate creation
    _console_handler = None
    _file_handler = None

    @staticmethod
    def setup_logging() -> None:
        """Configure the logging system based on current configuration.

        This method reads the logger configuration from the global Config singleton
        and sets up handlers, formatters, and log levels accordingly. It should be
        called once at application startup, but is also called automatically by
        logger() if needed.

        The method configures:
        - Root logger with WARNING level
        - Main application logger with configured level
        - Console output (if enabled)
        - File output (if enabled)
        - Component-specific log levels

        This method is idempotent - calling it multiple times has no effect
        after the initial setup.
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
        """Clean a string to make it suitable as a logger name.

        Removes or replaces characters that would be invalid in logger names,
        following Python's logging module conventions.

        Args:
            name: The string to clean

        Returns:
            A cleaned string suitable for use as a logger name
        """
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
        """Get a logger for the specified resource, optionally with a component name.

        Creates or retrieves a logger with a hierarchical name based on the resource URL
        and optional component. Automatically initializes logging if not already done.

        Args:
            resource: The resource to create a logger for
            component: Optional component name (e.g., "robots", "sitemaps")

        Returns:
            A logger instance configured according to application settings

        Example:
            >>> from ethicrawl.core import Resource
            >>> resource = Resource("https://example.com")
            >>> logger = Logger.logger(resource, "http")
            >>> logger.debug("Processing %s", resource.url)
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
        """Reset logging configuration to initial state.

        Removes all handlers and resets the initialization flag,
        allowing logging to be reconfigured. Primarily used for testing.

        Example:
            >>> # In a test setup
            >>> def setUp(self):
            >>>     Logger.reset()  # Ensure clean logging state
        """
        Logger._initialized = False
        Logger._console_handler = None
        Logger._file_handler = None

        # Reset the root logger
        root = getLogger()
        for handler in root.handlers[:]:
            root.removeHandler(handler)
