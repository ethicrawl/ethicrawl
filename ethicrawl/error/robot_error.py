from .ethicrawl_error import EthicrawlError


class RobotDisallowedError(EthicrawlError):
    """Raised when a resource is disallowed by robots.txt"""

