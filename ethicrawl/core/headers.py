from __future__ import annotations
from typing import Any, Mapping, TypeVar, cast


class Headers(dict):
    """HTTP headers container with case-insensitive key access.

    This class extends the standard dictionary to provide case-insensitive
    access to HTTP header keys, conforming to HTTP specifications. It ensures
    proper type handling and provides flexible initialization from various
    header sources.

    Attributes:
        Inherits all dictionary attributes

    Examples:
        >>> headers = Headers({"Content-Type": "text/html"})
        >>> headers["content-type"]
        'text/html'
        >>> headers["CONTENT-TYPE"] = "application/json"
        >>> headers["content-type"]
        'application/json'
        >>> "content-type" in headers
        True
        >>> "CONTENT-TYPE" in headers
        True
    """

    def __init__(self, headers: "Headers" | Mapping[str, Any] | None = None, **kwargs):
        """Initialize headers from a dictionary, dict-like object, or keyword arguments.

        Args:
            headers: Optional dictionary, Headers instance, or any dict-like object
            **kwargs: Optional keyword arguments to add as headers

        Raises:
            TypeError: If headers is not a dict-like object with an items() method
        """
        super().__init__()  # Start with empty dict

        # Handle dictionary or Headers initialization
        if headers is not None:
            # Check if it has items() method rather than strict type checking
            if not hasattr(headers, "items") or not callable(headers.items):
                raise TypeError(
                    f"Expected dict-like object, got {type(headers).__name__}"
                )

            for k, v in headers.items():
                self[k] = v

        # Add any keyword arguments
        for k, v in kwargs.items():
            self[k] = v

    def __getitem__(self, key):
        """Get header value with case-insensitive key access.

        Args:
            key: Header name (case-insensitive)

        Returns:
            The header value

        Raises:
            TypeError: If key is not a string
            KeyError: If header doesn't exist
        """
        if not isinstance(key, str):
            raise TypeError(f"Header keys must be strings, got {type(key).__name__}")
        return super().__getitem__(key.lower())

    def __setitem__(self, key: str, value: str | None) -> None:
        """Set header value with case-insensitive key storage.

        Setting a header to None will remove it from the collection.
        Non-string values are automatically converted to strings.

        Args:
            key: Header name (will be converted to lowercase)
            value: Header value, or None to remove the header

        Raises:
            TypeError: If key is not a string
        """
        if not isinstance(key, str):
            raise TypeError(f"Header keys must be strings, got {type(key).__name__}")
        key = key.lower()
        if value is None:
            self.pop(key, None)  # Remove the key if value is None
        else:
            # Convert non-string values to strings (matching requests behavior)
            if not isinstance(value, str):
                value = str(value)
            super().__setitem__(key, value)

    def __contains__(self, key):
        """Check if header exists with case-insensitive comparison.

        Args:
            key: Header name to check (case-insensitive)

        Returns:
            True if header exists, False otherwise
        """
        if not isinstance(key, str):
            return False
        return super().__contains__(key.lower())

    def get(self, key, default=None) -> str | None:
        """Get header value with optional default.

        Args:
            key: Header name (case-insensitive)
            default: Value to return if header doesn't exist

        Returns:
            Header value if it exists, otherwise the default value
        """
        if not isinstance(key, str):
            return default  # need a test here also
        try:
            return self[key]  # Use case-insensitive __getitem__
        except KeyError:
            return default
