import logging
import urllib.parse
import re
from typing import Optional


class Logger:
    """Factory class for creating and retrieving loggers for EthiCrawl instances."""

    @staticmethod
    def _clean_name(name: str) -> str:
        """Clean a string to make it suitable as a logger name."""
        # Replace invalid characters with underscores
        name = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", name)
        # Replace consecutive dots with a single dot
        name = re.sub(r"\.{2,}", ".", name)
        # Remove leading and trailing dots
        name = re.sub(r"^\.|\.$", "", name)
        return name or "unnamed"

    @staticmethod
    def logger(url: str, component: Optional[str] = None) -> logging.Logger:
        """
        Get a logger for the specified URL, optionally with a component name.

        Args:
            url: The URL to create a logger for
            component: Optional component name (e.g., "robots", "sitemaps")
            prefix: Namespace prefix for the logger

        Returns:
            A logger instance
        """

        prefix = __name__.split(".")[0]
        parsed = urllib.parse.urlparse(url)

        if not (parsed.scheme and parsed.netloc):
            raise ValueError(f"Invalid URL format: {url}")

        # Replace dots in domain with underscores to maintain proper hierarchy
        domain = parsed.netloc.replace(".", "_")

        # Build the logger name
        if component:
            logger_name = f"{prefix}.{domain}.{component}"
        else:
            logger_name = f"{prefix}.{domain}"

        # Clean the name for logger compatibility
        logger_name = Logger._clean_name(logger_name)

        # Get or create the logger
        return logging.getLogger(logger_name)
