from .ethicrawl_error import EthicrawlError


class DomainResolutionError(EthicrawlError):
    """Raised when a domain cannot be resolved through DNS.

    This error occurs when a hostname in a URL cannot be resolved to an IP address,
    typically indicating network connectivity issues or a non-existent domain.

    Attributes:
        url: The URL that was attempted to be accessed
        hostname: The specific hostname that could not be resolved
    """

    def __init__(self, url, hostname):
        self.url = url
        self.hostname = hostname
        message = f"Cannot resolve hostname '{hostname}' for URL '{url}'"
        super().__init__(message)
