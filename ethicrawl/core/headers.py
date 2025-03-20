class Headers(dict):
    """
    Custom dictionary for HTTP headers with type validation.

    Keys must be strings. Values can be strings or objects with string
    representations. Values of None remove the header.
    """

    def __setitem__(self, key: str, value: str | None) -> None:
        if not isinstance(key, str):
            raise TypeError(f"Header keys must be strings, got {type(key).__name__}")

        if value is None:
            self.pop(key, None)  # Remove the key if value is None
        else:
            # Convert non-string values to strings (matching requests behavior)
            if not isinstance(value, str):
                value = str(value)
            super().__setitem__(key, value)

    def __init__(self, headers=None, **kwargs):
        super().__init__()  # Start with empty dict

        # Handle dictionary or dict-like initialization
        if headers is not None:
            try:
                # This will work for both dict and dict-like objects with items()
                for k, v in headers.items():
                    self[k] = v  # Use our __setitem__ for validation
            except AttributeError:
                # If it doesn't have .items() method, try converting to dict first
                for k, v in dict(headers).items():
                    self[k] = v

        # Handle keyword arguments
        for k, v in kwargs.items():
            self[k] = v  # Use our __setitem__ for validation
