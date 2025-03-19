import pytest

from ethicrawl.robots import Robot, RobotFactory
from ethicrawl.context import Context
from ethicrawl.core import Url, Resource


class TestRobotFactory:

    def test_robotify(self):
        urls = [
            "https://example.com",
            "https://example.com/",
            "https://example.com/foo",
        ]
        for url in urls:
            assert RobotFactory.robotify(Url(url)) == "https://example.com/robots.txt"
        with pytest.raises(TypeError, match="Expected Url object"):
            RobotFactory.robotify(urls[-1])

    def test_robot_create(self):
        url = "https://www.example.com"
        context = Context(Resource(Url(url)))
        assert isinstance(RobotFactory.robot(context), Robot)
        with pytest.raises(TypeError, match="Expected Context object"):
            RobotFactory.robot("foo")
