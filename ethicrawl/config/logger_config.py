import logging
from dataclasses import dataclass, field

from .base_config import BaseConfig


@dataclass
class LoggerConfig(BaseConfig):
    """Logging configuration for Ethicrawl.

    Controls all aspects of Ethicrawl's logging system including output
    destinations, format, levels, and component-specific settings.

    The class provides validation for all settings and supports both numeric
    and string-based log levels (e.g., "DEBUG" or logging.DEBUG).

    Attributes:
        level: Default log level for all components (default: INFO)
        console_enabled: Whether to log to console (default: True)
        file_enabled: Whether to write logs to a file (default: False)
        file_path: Path where log file should be written (default: None)
        use_colors: Whether to use colored console output (default: True)
        format: Log message format string
        component_levels: Dictionary of component-specific log levels

    Example:
        >>> from ethicrawl.config import Config
        >>> config = Config()
        >>> # Set global log level
        >>> config.logger.level = "DEBUG"
        >>> # Enable file logging
        >>> config.logger.file_enabled = True
        >>> config.logger.file_path = "ethicrawl.log"
        >>> # Set component-specific level
        >>> config.logger.set_component_level("robots", "DEBUG")
        >>> config.logger.set_component_level("http", "WARNING")
    """

    # Private fields for property implementation
    _level: int = field(default=logging.INFO, repr=False)
    _console_enabled: bool = field(default=True, repr=False)
    _file_enabled: bool = field(default=False, repr=False)
    _file_path: str | None = field(default=None, repr=False)
    _use_colors: bool = field(default=True, repr=False)
    _component_levels: dict[str, int] = field(default_factory=dict, repr=False)
    _format: str = field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", repr=False
    )

    def __post_init__(self):
        # Validate initial values by calling setters
        self.level = self._level
        self.console_enabled = self._console_enabled
        self.file_enabled = self._file_enabled
        self.file_path = self._file_path
        self.use_colors = self._use_colors
        self.format = self._format

        # Component levels don't need validation via setter since
        # they'll be validated when added via set_component_level

    @property
    def level(self) -> int:
        """Default log level for all loggers.

        Can be set using either integer constants from the logging module
        or string names like "DEBUG", "INFO", etc.

        Default: logging.INFO (20)

        Raises:
            TypeError: If value is not an integer or string
            ValueError: If value is an invalid level
        """
        return self._level

    @level.setter
    def level(self, value: int | str):
        self._level = self._validate_log_level(value)

    @property
    def console_enabled(self) -> bool:
        """Whether to log to console/stdout.

        When True, log messages will be printed to the console.
        Default: True

        Raises:
            TypeError: If value is not a boolean
        """
        return self._console_enabled

    @console_enabled.setter
    def console_enabled(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(
                f"console_enabled must be a boolean, got {type(value).__name__}"
            )
        self._console_enabled = value

    @property
    def file_enabled(self) -> bool:
        """Whether to log to a file.

        When True, log messages will be written to the file specified
        by file_path (which must also be set).
        Default: False

        Raises:
            TypeError: If value is not a boolean
        """
        return self._file_enabled

    @file_enabled.setter
    def file_enabled(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(
                f"file_enabled must be a boolean, got {type(value).__name__}"
            )
        self._file_enabled = value

    @property
    def file_path(self) -> str | None:
        """Path to log file.

        Only used when file_enabled is True.
        Default: None

        Raises:
            TypeError: If value is not a string or None
        """
        return self._file_path

    @file_path.setter
    def file_path(self, value: str | None):
        if value is not None and not isinstance(value, str):
            raise TypeError(
                f"file_path must be a string or None, got {type(value).__name__}"
            )
        self._file_path = value

    @property
    def use_colors(self) -> bool:
        """Whether to use colorized output for console logging.

        When True, different log levels will be displayed in different
        colors in terminal output for better readability.
        Default: True

        Raises:
            TypeError: If value is not a boolean
        """
        return self._use_colors

    @use_colors.setter
    def use_colors(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(f"use_colors must be a boolean, got {type(value).__name__}")
        self._use_colors = value

    @property
    def format(self) -> str:
        """Log message format string.

        Uses Python's logging format string syntax.
        Default: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        Raises:
            TypeError: If value is not a string
            ValueError: If value is empty
        """
        return self._format

    @format.setter
    def format(self, value: str):
        if not isinstance(value, str):
            raise TypeError(f"format must be a string, got {type(value).__name__}")
        if not value:
            raise ValueError("format string cannot be empty")
        self._format = value

    @property
    def component_levels(self) -> dict[str, int]:
        """Special log levels for specific components.

        Returns a dictionary mapping component names to log levels.
        Note: Returns a copy to prevent direct mutation.

        Example:
            >>> config.logger.component_levels
            {'robots': 10, 'http': 30}
        """
        return self._component_levels.copy()  # Return a copy to prevent direct mutation

    def set_component_level(self, component_name: str, level: int | str) -> None:
        """Set a specific log level for a component.

        Args:
            component_name: The component name (e.g., "robots", "sitemaps")
            level: The log level (can be int or level name string)

        Raises:
            TypeError: If level is not an integer or string
            ValueError: If string level name is not valid

        Example:
            >>> config.logger.set_component_level("robots", "DEBUG")
            >>> config.logger.set_component_level("http", logging.WARNING)
        """
        validated_level = self._validate_log_level(level)
        self._component_levels[component_name] = validated_level

    def _validate_log_level(self, level: int | str) -> int:
        """
        Validate and convert a log level value.

        Args:
            level: The log level (can be int or level name string)

        Returns:
            int: The validated integer log level

        Raises:
            TypeError: If level is not an integer or string
            ValueError: If the level is invalid
        """
        # Check type
        if not isinstance(level, (int, str)):
            raise TypeError(
                f"Log level must be an integer or level name string, got {type(level).__name__}"
            )

        # Handle string conversion
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        valid_levels = ", ".join(level_map.keys())
        if isinstance(level, str):

            if level.upper() in level_map:
                level = level_map[level.upper()]
            else:
                raise ValueError(
                    f"Invalid log level name: '{level}'. Valid levels are: {valid_levels}"
                )

        # Validate integer value
        elif level not in [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ]:
            valid_values = ", ".join(
                [f"{name} ({value})" for value, name in level_map.items()]
            )
            raise ValueError(
                f"Invalid integer log level: {level}. Valid values are: {valid_values}"
            )

        return level

    def to_dict(self) -> dict:
        """Convert logger configuration to a dictionary."""
        return {
            "level": self._level,
            "console_enabled": self._console_enabled,
            "file_enabled": self._file_enabled,
            "file_path": self._file_path,
            "use_colors": self._use_colors,
            "format": self._format,
            # Return a copy to prevent direct mutation
            "component_levels": self._component_levels.copy(),
        }
