import threading
import copy
import json
from dataclasses import dataclass, field
from typing import Dict
from .http_config import HttpConfig
from .logger_config import LoggerConfig


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
    """Main application configuration"""

    http: HttpConfig = field(default_factory=HttpConfig)
    logger: LoggerConfig = field(default_factory=LoggerConfig)

    # Thread safety helpers
    _lock = threading.RLock()

    def get_snapshot(self):
        """
        Get a deep copy of the current configuration.

        This is useful for thread pools that need a stable configuration
        that won't change even if the main config is modified.
        """
        with self._lock:
            return copy.deepcopy(self)

    def update(self, config_dict):
        """Thread-safe update of multiple config values."""
        with self._lock:
            for section, values in config_dict.items():
                # Skip private attributes
                if section.startswith("_"):
                    continue

                if hasattr(self, section):
                    section_obj = getattr(self, section)
                    if isinstance(values, dict):
                        for k, v in values.items():
                            # Skip private attributes
                            if k.startswith("_"):
                                continue

                            if hasattr(section_obj, k):
                                setattr(section_obj, k, v)

    @classmethod
    def reset(cls):
        """Reset the singleton instance (useful for testing)"""
        with cls.__class__._lock:
            if cls in cls.__class__._instances:
                del cls.__class__._instances[cls]

    def to_dict(self):
        """
        Convert the configuration to a dictionary suitable for serialization.
        Includes both instance attributes and property values.

        Returns:
            dict: A dictionary representation of the config, excluding private attributes.
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
                        try:
                            section_dict[prop_name] = getattr(section_value, prop_name)
                        except Exception:
                            # Skip properties that can't be accessed
                            pass

                result[section_name] = section_dict
            else:
                # Handle simple values
                result[section_name] = section_value

        return result

    def __str__(self):
        """Return a string representation of the config."""
        import json

        return json.dumps(self.to_dict(), indent=2)
