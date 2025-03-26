"""Client interfaces for making ethical requests to resources."""

from .client import Client, NoneClient
from .request import Request
from .response import Response
from .transport import Transport

__all__ = [
    "Client",
    "NoneClient",
    "Request",
    "Response",
    "Transport",
]
