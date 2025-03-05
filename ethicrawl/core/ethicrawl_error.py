from ethicrawl.logger import Logger


class EthiCrawlError(Exception):
    """Base exception for all EthiCrawl errors."""

    def __init__(self, message="", url=None):
        self.message = message
        self.url = url

        # Log the exception if we have URL context
        if url:
            logger = Logger.logger(url, "error")
            logger.error(f"EthiCrawlError: {message}")

        # Call the base class constructor
        super().__init__(message)

    def __str__(self):
        if self.url:
            return f"{self.message} (URL: {self.url})"
        return self.message
