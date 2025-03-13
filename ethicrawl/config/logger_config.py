from dataclasses import dataclass, field
from typing import Optional, Dict, List, Union
import logging


@dataclass
class LoggerConfig:
    """Logging configuration for Ethicrawl"""

    # Private fields for property implementation
    _level: int = field(default=logging.INFO, repr=False)
    _console_enabled: bool = field(default=True, repr=False)
    _file_enabled: bool = field(default=False, repr=False)
    _file_path: Optional[str] = field(default=None, repr=False)
    _use_colors: bool = field(default=True, repr=False)
    _component_levels: Dict[str, int] = field(default_factory=dict, repr=False)
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
        """Default log level for all loggers"""
        return self._level

    @level.setter
    def level(self, value: Union[int, str]):
        # Boolean is a subclass of int, so we need to check for it explicitly
        if isinstance(value, bool) or not isinstance(value, (int, str)):
            raise TypeError("Log level must be an integer or level name string")

        # Convert string level names to integers
        if isinstance(value, str):
            level_map = {
                "DEBUG": logging.DEBUG,
                "INFO": logging.INFO,
                "WARNING": logging.WARNING,
                "ERROR": logging.ERROR,
                "CRITICAL": logging.CRITICAL,
            }
            if value.upper() in level_map:
                value = level_map[value.upper()]
            else:
                raise ValueError(f"Unknown log level: {value}")

        # Value should now be an integer
        self._level = value

    @property
    def console_enabled(self) -> bool:
        """Whether to log to console/stdout"""
        return self._console_enabled

    @console_enabled.setter
    def console_enabled(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("console_enabled must be a boolean")
        self._console_enabled = value

    @property
    def file_enabled(self) -> bool:
        """Whether to log to a file"""
        return self._file_enabled

    @file_enabled.setter
    def file_enabled(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("file_enabled must be a boolean")
        self._file_enabled = value

    @property
    def file_path(self) -> Optional[str]:
        """Path to log file (None = no file logging)"""
        return self._file_path

    @file_path.setter
    def file_path(self, value: Optional[str]):
        if value is not None and not isinstance(value, str):
            raise TypeError("file_path must be a string or None")
        self._file_path = value

    @property
    def use_colors(self) -> bool:
        """Whether to use colorized output for console logging"""
        return self._use_colors

    @use_colors.setter
    def use_colors(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("use_colors must be a boolean")
        self._use_colors = value

    @property
    def format(self) -> str:
        """Log message format string"""
        return self._format

    @format.setter
    def format(self, value: str):
        if not isinstance(value, str):
            raise TypeError("format must be a string")
        if not value:
            raise ValueError("format string cannot be empty")
        self._format = value

    @property
    def component_levels(self) -> Dict[str, int]:
        """Special log levels for specific components"""
        return self._component_levels.copy()  # Return a copy to prevent direct mutation

    def set_component_level(self, component_name: str, level: Union[int, str]) -> None:
        """
        Set a specific log level for a component

        Args:
            component_name: The component name (e.g., "robots", "sitemaps")
            level: The log level (can be int or level name string)

        Raises:
            TypeError: If level is not an integer or string
            ValueError: If string level name is not valid
        """
        # Boolean is a subclass of int in Python, so check for it explicitly
        if isinstance(level, bool) or not isinstance(level, (int, str)):
            raise TypeError("Log level must be an integer or level name string")

        # Convert string level names to integers
        if isinstance(level, str):
            level_map = {
                "DEBUG": logging.DEBUG,
                "INFO": logging.INFO,
                "WARNING": logging.WARNING,
                "ERROR": logging.ERROR,
                "CRITICAL": logging.CRITICAL,
            }
            if level.upper() in level_map:
                level = level_map[level.upper()]
            else:
                raise ValueError(f"Unknown log level: {level}")

        # Value should now be an integer
        self._component_levels[component_name] = level
