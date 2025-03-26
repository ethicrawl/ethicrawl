from abc import ABC, abstractmethod
from json import dumps
from typing import Any


class BaseConfig(ABC):
    """Abstract base class for configuration components.

    All configuration classes inherit from this class to ensure
    a consistent interface and behavior across the configuration system.
    Configuration objects can be converted to dictionaries, serialized,
    and represented as strings with consistent formatting.

    Example:
        >>> from abc import ABC
        >>> from ethicrawl.config import BaseConfig
        >>>
        >>> class MyConfig(BaseConfig):
        ...     def __init__(self, name="default", value=42):
        ...         self.name = name
        ...         self.value = value
        ...
        ...     def to_dict(self) -> dict:
        ...         return {"name": self.name, "value": self.value}
        >>>
        >>> config = MyConfig("test", 100)
        >>> config.to_dict()
        {'name': 'test', 'value': 100}
        >>> print(config)
        {
          "name": "test",
          "value": 100
        }
    """

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to a dictionary representation.

        Implementations must produce a JSON-serializable dictionary
        that fully represents the configuration state.

        Returns:
            Dictionary representation of the configuration
        """

    def __repr__(self) -> str:
        """Default string representation showing config values.

        Returns:
            String in format ClassName({config values})
        """
        return str()

    def __str__(self) -> str:
        """Human-readable string representation.

        Returns:
            Pretty-printed JSON representation of the configuration
        """
        return str()
