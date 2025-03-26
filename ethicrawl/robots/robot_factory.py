from ethicrawl.context import Context
from ethicrawl.core import Url

from .robot import Robot


class RobotFactory:
    """Factory for creating Robot instances and robots.txt URLs.

    This utility class provides methods for:
    - Converting site URLs to robots.txt URLs
    - Creating properly initialized Robot instances from a Context

    Using this factory ensures consistent Robot creation throughout the
    application and handles the necessary URL transformations.
    """

    @staticmethod
    def robotify(url: Url) -> Url:
        """Convert a site URL to its corresponding robots.txt URL.

        Takes any URL and transforms it to the canonical robots.txt URL
        by extracting the base URL and appending "robots.txt".

        Args:
            url: The site URL to convert

        Returns:
            A new Url pointing to the site's robots.txt file

        Raises:
            TypeError: If url is not a Url instance

        Example:
            >>> from ethicrawl.core import Url
            >>> from ethicrawl.robots import RobotFactory
            >>> site = Url("https://example.com/some/page")
            >>> robots_url = RobotFactory.robotify(site)
            >>> str(robots_url)
            'https://example.com/robots.txt'
        """
        if not isinstance(url, Url):
            raise TypeError(f"Expected Url object, got {type(url).__name__}")
        return Url(url.base).extend("robots.txt")

    @staticmethod
    def robot(context: Context) -> Robot:
        """Create a Robot instance from a Context.

        Extracts the URL from the context's resource, converts it to a
        robots.txt URL, and creates a new Robot instance bound to that URL
        and the provided context.

        Args:
            context: The context to use for the Robot

        Returns:
            A fully initialized Robot instance

        Raises:
            TypeError: If context is not a Context instance

        Example:
            >>> from ethicrawl.context import Context
            >>> from ethicrawl.core import Resource
            >>> from ethicrawl.robots import RobotFactory
            >>> ctx = Context(Resource("https://example.com"))
            >>> robot = RobotFactory.robot(ctx)
            >>> robot.can_fetch("https://example.com/page")
            True
        """
        if not isinstance(context, Context):
            raise TypeError(f"Expected Context object, got {type(context).__name__}")
        return Robot(RobotFactory.robotify(context.resource.url), context)
