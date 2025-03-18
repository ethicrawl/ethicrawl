from abc import ABC, abstractmethod
from json import dumps
from typing import Dict, Any


class BaseConfig(ABC):
    """
    Abstract base class for configuration components.

    All configuration classes should inherit from this class to ensure
    a consistent interface and behavior across the configuration system.
    """

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:  # pragma: no cover
        """
        Convert configuration to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of the configuration.
                The dictionary should be JSON-serializable.
        """
        pass

    def __repr__(self) -> str:
        """Default string representation showing config values."""
        return f"{self.__class__.__name__}({self.to_dict()})"

    def __str__(self) -> str:
        """String representation suitable for debugging."""
        return dumps(self.to_dict(), indent=2)
