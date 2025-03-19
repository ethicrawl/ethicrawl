from ethicrawl.core import EthicrawlError


class RobotDisallowedError(EthicrawlError):
    """Raised when a resource is disallowed by robots.txt"""

    pass
