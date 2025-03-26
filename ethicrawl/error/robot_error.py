from .ethicrawl_error import EthicrawlError


class RobotDisallowedError(EthicrawlError):
    """Raised when a URL is disallowed by robots.txt rules.

    This exception indicates that the requested URL cannot be accessed
    because it is explicitly disallowed by the site's robots.txt file.

    Attributes:
        url: The URL that was disallowed
        robot_url: The URL of the robots.txt file that disallowed access
    """
