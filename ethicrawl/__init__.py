"""
Ethicrawl - An ethical web crawler that respects robots.txt and rate limits.

This package provides tools for crawling websites in an ethical manner,
following robots.txt rules and maintaining reasonable request rates.
"""

from ethicrawl.core.ethicrawl import Ethicrawl
from ethicrawl.client.http_client import HttpClient
from ethicrawl.core.url import Url
from ethicrawl.core.resource import Resource
from ethicrawl.core.resource_list import ResourceList
from ethicrawl.config import Config

__version__ = "1.0.0-alpha"

__all__ = [
    "Ethicrawl",  # Main crawler facade
    "HttpClient",  # HTTP client for direct requests
    "Url",  # URL handling
    "Resource",  # Resource abstraction
    "ResourceList",  # Resources
    "Config",  # Global configuration
]
