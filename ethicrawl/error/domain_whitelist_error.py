from .ethicrawl_error import EthicrawlError


class DomainWhitelistError(EthicrawlError):
    """Raised when attempting to access a non-whitelisted domain.

    This error occurs when a request is made to a domain that differs
    from the primary bound domain and hasn't been explicitly whitelisted.

    Attributes:
        url: URL that was attempted to be accessed
        bound_domain: The domain the ethicrawl is bound to
    """

    def __init__(self, url):
        self.url = url
        message = f"Cannot access URL '{url}' - domain not whitelisted.'"
        super().__init__(message)
