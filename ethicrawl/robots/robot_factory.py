from ethicrawl.context import Context
from ethicrawl.core import Url

from .robot import Robot


class RobotFactory:
    @staticmethod
    def robotify(url: Url) -> Url:
        if not isinstance(url, Url):
            raise TypeError(f"Expected Url object, got {type(url).__name__}")
        return Url(url.base).extend("robots.txt")

    @staticmethod
    def robot(context: Context) -> Robot:
        if not isinstance(context, Context):
            raise TypeError(f"Expected Context object, got {type(context).__name__}")
        return Robot(RobotFactory.robotify(context.resource.url), context)
