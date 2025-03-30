from dataclasses import dataclass, field

from ethicrawl.context import Context
from ethicrawl.robots import Robot, RobotFactory


@dataclass
class DomainContext:
    """Represents a whitelisted domain with its context and robot handler.

    DomainContext maintains domain-specific information including:
    - Connection to a Context instance for making requests
    - Lazy-loaded Robot instance for robots.txt handling

    This class serves as a container for domain-specific components and
    provides lazy initialization for resources that are expensive to create
    until they're needed.

    Attributes:
        context: Context instance for this domain
        _robot: Internal storage for lazy-loaded Robot instance

    Example:
        >>> from ethicrawl.core import Resource, Url
        >>> from ethicrawl.context import Context
        >>> from ethicrawl.domain_context import DomainContext
        >>>
        >>> # Create a context for example.com
        >>> url = Url("https://example.com")
        >>> context = Context(Resource(url))
        >>>
        >>> # Create domain context
        >>> domain = DomainContext(context)
        >>>
        >>> # Access robot (creates it on first access)
        >>> robot = domain.robot
        >>> allowed = robot.can_fetch("https://example.com/page")
    """

    context: Context
    _robot: Robot | None = field(default=None, repr=False)

    @property
    def robot(self) -> Robot:
        """Get the robots.txt handler for this domain.

        Lazily initializes the Robot instance on first access
        to avoid unnecessary network requests until needed.

        Returns:
            Robot instance configured for this domain
        """
        if self._robot is None:
            self._robot = RobotFactory.robot(self.context)
        return self._robot
