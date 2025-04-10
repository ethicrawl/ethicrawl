from functools import wraps

from ethicrawl.core import Resource


def validate_resource(func):
    """Decorator that validates the first argument is a Resource instance."""

    @wraps(func)
    def wrapper(self, resource, *args, **kwargs):
        if not isinstance(resource, Resource):
            raise TypeError(f"Expected Resource, got {type(resource).__name__}")
        return func(self, resource, *args, **kwargs)

    return wrapper
