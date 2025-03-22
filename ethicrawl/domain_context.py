from dataclasses import dataclass, field

from ethicrawl.context import Context
from ethicrawl.robots import Robot, RobotFactory


@dataclass
class DomainContext:
    """Represents a whitelisted domain with its context and robot handler."""

    context: Context
    _robot: Robot | None = field(default=None, repr=False)

    @property
    def robot(self) -> Robot:
        """Lazy-load the robot handler when needed."""
        if self._robot is None:
            self._robot = RobotFactory.robot(self.context)
        return self._robot
