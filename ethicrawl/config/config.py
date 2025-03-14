import threading
import copy
import json
from dataclasses import dataclass, field
from typing import Dict, Any
from .http_config import HttpConfig
from .logger_config import LoggerConfig
from .sitemap_config import SitemapConfig


class SingletonMeta(type):
    """Metaclass to implement the Singleton pattern."""

    _instances: Dict = {}
    _lock = threading.RLock()  # Reentrant lock for thread safety

    def __call__(cls, *args, **kwargs):
        with cls._lock:  # Thread-safe singleton creation
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
            return cls._instances[cls]


@dataclass
class Config(metaclass=SingletonMeta):
    """
    Global configuration for Ethicrawl.

    A thread-safe singleton class that provides application-wide configuration settings.
    Use this to configure default behavior for HTTP clients, logging, and other components.

    Because this is a singleton, all imports of Config() will return the same instance,
    allowing configuration changes to be visible throughout the application.

    Examples:
        >>> from ethicrawl import Config
        >>> config = Config()
        >>> config.http.timeout = 60  # Set HTTP timeout
        >>> config.logger.level = "DEBUG"  # Set logging level

        # Configuration changes affect all parts of the application
        >>> from another_module import get_config
        >>> other_config = get_config()
        >>> other_config is config  # True - same instance

        # For thread pools, use snapshots
        >>> snapshot = config.get_snapshot()
        >>> config.http.timeout = 30  # Change won't affect snapshot
        >>> snapshot.http.timeout  # Still 60

    Attributes:
        http (HttpConfig): HTTP-related configuration
        logger (LoggerConfig): Logging configuration
    """

    http: HttpConfig = field(default_factory=HttpConfig)
    logger: LoggerConfig = field(default_factory=LoggerConfig)
    sitemap: SitemapConfig = field(default_factory=SitemapConfig)

    # Thread safety helpers
    _lock = threading.RLock()

    def get_snapshot(self):
        """
        Get a deep copy of the current configuration.

        This is useful for thread pools that need a stable configuration
        that won't change even if the main config is modified.

        Returns:
            Config: A deep copy of the configuration (not a singleton)

        Example:
            >>> config = Config()
            >>> config.http.timeout = 60
            >>> snapshot = config.get_snapshot()
            >>> config.http.timeout = 30
            >>> snapshot.http.timeout  # Still 60
        """
        with self._lock:
            return copy.deepcopy(self)

    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        Update configuration from a dictionary.

        This method allows bulk updates of configuration settings from
        a nested dictionary structure. Each top-level key should match
        a configuration section name.

        Args:
            config_dict (dict): Configuration values to update

        Example:
            >>> config = Config()
            >>> config.update({
            ...     'http': {'timeout': 120, 'rate_limit': 2.0},
            ...     'logger': {'level': 'INFO'}
            ... })
            >>> config.http.timeout  # 120

        Raises:
            AttributeError: If attempting to set an invalid configuration property
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
                        except AttributeError as e:
                            # Provide a more helpful error message
                            raise AttributeError(
                                f"Failed to set '{k}' on {section_name} config: {e}"
                            )

    @classmethod
    def reset(cls):
        """
        Reset configuration to default values.

        This removes the singleton instance, causing the next access to
        create a fresh instance with default values.

        Example:
            >>> config = Config()
            >>> config.http.timeout = 120
            >>> Config.reset()
            >>> new_config = Config()
            >>> new_config.http.timeout  # Back to default (10)
        """
        with cls.__class__._lock:
            if cls in cls.__class__._instances:
                del cls.__class__._instances[cls]

    def to_dict(self):
        """
        Convert configuration to a dictionary.

        Creates a nested dictionary representation of all configuration
        settings, suitable for serialization or storage.

        Returns:
            dict: Dictionary representation of the configuration

        Example:
            >>> config = Config()
            >>> config.http.timeout = 60
            >>> config_dict = config.to_dict()
            >>> config_dict['http']['timeout']  # 60
        """
        result = {}

        # Get all public attributes of this object
        for section_name, section_value in self.__dict__.items():
            # Skip private attributes
            if section_name.startswith("_"):
                continue

            # Handle config sections
            if hasattr(section_value, "__dict__") or hasattr(
                section_value.__class__, "__dataclass_fields__"
            ):
                section_dict = {}

                # Get normal instance attributes
                for key, value in section_value.__dict__.items():
                    if not key.startswith("_"):
                        section_dict[key] = value

                # Get property values by inspecting the class
                for prop_name in dir(section_value.__class__):
                    if not prop_name.startswith("_") and isinstance(
                        getattr(section_value.__class__, prop_name), property
                    ):
                        # Dont use try except, be explicit
                        if hasattr(section_value, prop_name):
                            section_dict[prop_name] = getattr(section_value, prop_name)

                result[section_name] = section_dict
            else:
                # Handle simple values
                result[section_name] = section_value

        return result

    def __str__(self):
        """
        Return a JSON string representation of the config.

        Returns:
            str: JSON string with pretty formatting

        Example:
            >>> config = Config()
            >>> print(config)
            {
              "http": {
                "timeout": 10,
                "rate_limit": 1.0
              },
              "logger": {
                "level": "INFO"
              }
            }
        """

        return json.dumps(self.to_dict(), indent=2)
