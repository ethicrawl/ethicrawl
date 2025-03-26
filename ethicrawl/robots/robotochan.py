from dataclasses import dataclass

from .robot import Robot


@dataclass
class RobotoChan(Robot):
    """Easter egg extension of Robot that provides encouragement.

    This class inherits all functionality from Robot while overriding
    the string representation with a Japanese phrase of encouragement.

    RobotoChan behaves identically to Robot for all practical purposes,
    but provides a more cheerful message when converted to a string.

    Example:
        >>> from ethicrawl.context import Context
        >>> from ethicrawl.core import Resource, Url
        >>> from ethicrawl.robots import RobotoChan
        >>> context = Context(Resource("https://example.com"))
        >>> roboto = RobotoChan(Url("https://example.com/robots.txt"), context)
        >>> str(roboto)
        '頑張ってください!'  # Japanese for "Keep doing your best!" or "Persevere!"
    """

    def __str__(self):
        """Return an encouraging message in Japanese.

        Returns:
            '頑張ってください!' - A Japanese phrase expressing sincere
            encouragement to persevere and do one's best.
        """
        return "頑張ってください!"
