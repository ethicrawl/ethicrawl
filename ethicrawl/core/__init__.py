"""Core types and utilities for resource identification and handling."""

from .headers import Headers
from .resource import Resource
from .resource_list import ResourceList
from .url import Url

__all__ = [
    "Headers",
    "Resource",
    "ResourceList",
    "Url",
]
