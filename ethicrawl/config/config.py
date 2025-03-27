import copy
import json
import threading
from dataclasses import dataclass, field
from typing import Any

from .http_config import HttpConfig
from .logger_config import LoggerConfig
from .sitemap_config import SitemapConfig


class SingletonMeta(type):
    """Metaclass to implement the Singleton pattern."""

    _instances: dict = {}
    _lock = threading.RLock()  # Reentrant lock for thread safety

    def __call__(cls, *args, **kwargs):
        with cls._lock:  # Thread-safe singleton creation
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
            return cls._instances[cls]


@dataclass
class Config(metaclass=SingletonMeta):
    """Global configuration singleton for Ethicrawl.

    This class provides a centralized, thread-safe configuration system
    for all components of Ethicrawl. It implements the Singleton pattern
    to ensure consistent settings throughout the application.

    The configuration is organized into sections (http, logger, sitemap)
    with each section containing component-specific settings.

    Thread Safety:
        All configuration updates are protected by a reentrant lock,
        ensuring thread-safe operation in multi-threaded crawling scenarios.

    Integration Features:
        - Convert to/from dictionaries for integration with external config systems
        - JSON serialization for storage or transmission
        - Hierarchical structure matches common config formats

    Attributes:
        http: HTTP-specific configuration (user agent, headers, timeout)
        logger: Logging configuration (levels, format, output)
        sitemap: Sitemap parsing configuration (limits, defaults)

    Example:
        >>> from ethicrawl.config import Config
        >>> config = Config()  # Get the global instance
        >>> config.http.user_agent = "MyCustomBot/1.0"
        >>> config.logger.level = "DEBUG"
        >>>
        >>> # Thread-safe update of multiple settings at once
        >>> config.update({
        ...     "http": {"timeout": 30},
        ...     "logger": {"component_levels": {"robots": "DEBUG"}}
        ... })
        >>>
        >>> # Get a snapshot for thread-safe reading
        >>> snapshot = config.get_snapshot()
        >>> print(snapshot.http.timeout)
        30
        >>>
        >>> # Export config for integration with external systems
        >>> config_dict = config.to_dict()
        >>> config_json = str(config)
    """

    http: HttpConfig = field(default_factory=HttpConfig)
    logger: LoggerConfig = field(default_factory=LoggerConfig)
    sitemap: SitemapConfig = field(default_factory=SitemapConfig)

    # Thread safety helpers
    _lock = threading.RLock()

    def get_snapshot(self) -> "Config":
        """Create a thread-safe deep copy of the current configuration.

        Returns:
            A deep copy of the current Config object
        """
        with self._lock:
            return copy.deepcopy(self)

    def update(self, config_dict: dict[str, Any]) -> None:
        """Update configuration from a dictionary.

        Updates configuration sections based on a nested dictionary structure.
        The dictionary should have section names as top-level keys and
        property-value pairs as nested dictionaries.

        Args:
            config_dict: Dictionary with configuration settings

        Raises:
            AttributeError: If trying to set a property that doesn't exist

        Example:
            >>> config.update({
            ...     "http": {
            ...         "user_agent": "CustomBot/1.0",
            ...         "timeout": 30
            ...     },
            ...     "logger": {
            ...         "level": "DEBUG"
            ...     }
            ... })
        """
        with self._lock:
            for section_name, section_dict in config_dict.items():
                if not hasattr(self, section_name):
                    continue

                section_obj = getattr(self, section_name)

                for k, v in section_dict.items():
                    # Special handling for component_levels
                    if section_name == "logger" and k == "component_levels":
                        # Use the set_component_level method instead of direct assignment
                        for component, level in v.items():
                            section_obj.set_component_level(component, level)
                    else:
                        # Check if the attribute exists before trying to set it
                        if not hasattr(section_obj.__class__, k) or not isinstance(
                            getattr(section_obj.__class__, k), property
                        ):
                            raise AttributeError(
                                f"No such property: '{k}' on {section_name} config"
                            )

                        try:
                            setattr(section_obj, k, v)
                        except AttributeError as exc:  # pragma: no cover
                            # Provide a more helpful error message
                            raise AttributeError(
                                f"Failed to set '{k}' on {section_name} config: {exc}"
                            ) from exc

    @classmethod
    def reset(cls):
        """Reset the singleton instance to default values.

        Removes the existing instance from the singleton registry,
        causing a new instance to be created on next access.

        Example:
            >>> Config.reset()  # Reset to defaults
            >>> config = Config()  # Get fresh instance
        """
        with cls.__class__._lock:
            if cls in cls.__class__._instances:
                del cls.__class__._instances[cls]

    def to_dict(self) -> dict:
        """Convert the configuration to a dictionary.

        Returns:
            A nested dictionary representing all configuration sections
        """
        result = {}

        # Get all public attributes of this object
        for section_name, section_value in self.__dict__.items():
            # Skip private attributes
            if section_name.startswith("_"):
                continue

            # All sections should have to_dict() method
            result[section_name] = section_value.to_dict()

        return result

    def __str__(self) -> str:
        """Format the configuration as a JSON string.

        Returns:
            Formatted JSON representation of the configuration
        """
        return json.dumps(self.to_dict(), indent=2)
