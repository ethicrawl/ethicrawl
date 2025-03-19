from ethicrawl.robots.robotochan import *
from ethicrawl.context import Context
from ethicrawl.core import Resource
from ethicrawl.client.http import HttpClient

client = HttpClient()
context = Context(Resource("https://www.bbc.co.uk"), client)

robot = RobotFactory.robot(context)

# dir(robot.url)
print(robot.url, robot.context)
