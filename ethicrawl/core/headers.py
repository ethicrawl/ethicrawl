class Headers(dict):
    """
    Custom dictionary for HTTP headers with type validation.

    Keys must be strings. Values can be strings or objects with string
    representations. Values of None remove the header.
    """

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError(f"Header keys must be strings, got {type(key).__name__}")

        if value is None:
            self.pop(key, None)  # Remove the key if value is None
        else:
            # Convert non-string values to strings (matching requests behavior)
            if not isinstance(value, str):
                value = str(value)
            super().__setitem__(key, value)

    def __init__(self, *args, **kwargs):
        super().__init__()  # Start with empty dict

        # Handle dictionary initialization
        if args and isinstance(args[0], dict):
            for k, v in args[0].items():
                self[k] = v  # Use our __setitem__ for validation

        # Handle keyword arguments
        for k, v in kwargs.items():
            self[k] = v  # Use our __setitem__ for validation
