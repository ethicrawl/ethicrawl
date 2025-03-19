from ethicrawl.context import Context
from ethicrawl.core import Url

from .robot import Robot


class RobotFactory:
    @staticmethod
    def robotify(url: Url) -> Url:
        if not isinstance(url, Url):
            raise TypeError("Expected Url object")
        return Url(url.base).extend("robots.txt")

    @staticmethod
    def robot(context: Context) -> Robot:
        if not isinstance(context, Context):
            raise TypeError("Expected Context object")
        return Robot(RobotFactory.robotify(context.resource.url), context)
