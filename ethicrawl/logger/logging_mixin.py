from typing import Optional
from ethicrawl.logger.logger import Logger


class LoggingMixin:
    """
    Mixin to add logging capabilities to any class.

    Usage:
        class MyClass(LoggingMixin):
            def __init__(self, url):
                self._setup_logger(url)

            def do_something(self):
                self._logger.info("Doing something")
    """

    def _setup_logger(self, url: str, component: Optional[str] = None) -> None:
        """
        Set up a logger for this instance.

        Args:
            url: Base URL for logging context
            component: Optional component name (defaults to class name lowercase)
        """
        if not hasattr(self, "_logger"):
            # Default to class name as component if not provided
            if component is None:
                component = self.__class__.__name__.lower()

            self._logger = Logger.logger(url, component)
