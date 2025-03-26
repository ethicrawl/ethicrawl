class EthicrawlError(Exception):
    """Base exception class for all Ethicrawl-specific errors.

    This class serves as the parent for all custom exceptions raised by
    the Ethicrawl library. By catching this exception type, client code
    can handle all Ethicrawl-specific errors while allowing other exceptions
    to propagate normally.

    Example:
        >>> try:
        ...     crawler.get("https://example.com/disallowed")
        ... except EthicrawlError as e:
        ...     print(f"Ethicrawl error: {e}")
    """

    pass
