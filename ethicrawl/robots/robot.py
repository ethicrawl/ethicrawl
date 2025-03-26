from dataclasses import dataclass

from protego import Protego  # type: ignore  # No type stubs available for this package

from ethicrawl.config import Config
from ethicrawl.context import Context
from ethicrawl.core import Resource, ResourceList, Url
from ethicrawl.error import RobotDisallowedError
from ethicrawl.sitemaps import IndexEntry


@dataclass
class Robot(Resource):
    """Representation of a site's robots.txt file with permission checking.

    This class handles fetching, parsing, and enforcing robots.txt rules according to
    the Robots Exclusion Protocol. It follows standard robots.txt behavior:
    - 404 response: allow all URLs (fail open)
    - 200 response: parse and enforce rules in the robots.txt file
    - Other responses (5xx, etc.): deny all URLs (fail closed)

    As a Resource subclass, Robot maintains the URL identity of the robots.txt file
    while providing methods to check permissions and access sitemap references.

    Attributes:
        url: URL of the robots.txt file (inherited from Resource)
        context: Context with client for making requests

    Example:
        >>> from ethicrawl.context import Context
        >>> from ethicrawl.core import Resource, Url
        >>> from ethicrawl.robots import Robot
        >>> from ethicrawl.client.http import HttpClient
        >>> client = HttpClient()
        >>> context = Context(Resource("https://example.com"), client)
        >>> robot = Robot(Url("https://example.com/robots.txt"), context)
        >>> robot.can_fetch("https://example.com/allowed")
        True
    """

    _context: Context

    def __post_init__(self):
        """Initialize the robot instance and fetch robots.txt.

        Fetches the robots.txt file using the provided context's client,
        then parses it according to response status:
        - 404: Create empty ruleset (allow all)
        - 200: Parse actual robots.txt content
        - Other: Create restrictive ruleset (deny all)
        """
        super().__post_init__()
        self._logger = self._context.logger("robots")
        self._logger.debug("Robot instance initialized for %s", self.url)
        response = self._context.client.get(Resource(self.url))
        if not hasattr(response, "status_code"):
            status_code = None
        else:
            status_code = (
                response.status_code  # pyright: ignore[reportAttributeAccessIssue]
            )
        if status_code == 404:  # spec says fail open
            self._parser = Protego.parse("")
            self._logger.info("Server returned %s - allowing all", status_code)
        elif status_code == 200:  # there's a robots.txt to use
            self._parser = Protego.parse(
                response.text  # pyright: ignore[reportAttributeAccessIssue]
            )
            self._logger.info("Server returned %s - using robots.txt", status_code)
        else:
            self._parser = Protego.parse("User-agent: *\nDisallow: /")
            self._logger.warning("Server returned %s - denying all", status_code)

    @property
    def context(self) -> Context:
        """Get the context associated with this robot.

        Returns:
            The context object containing client and other settings
        """
        return self._context

    def can_fetch(
        self, resource: Resource | Url | str, user_agent: str | None = None
    ) -> bool:
        """Check if a URL can be fetched according to robots.txt rules.

        Args:
            resource: The URL to check against robots.txt rules
            user_agent: Optional user agent string to use for checking.
                If not provided, uses client's user_agent or config default.

        Returns:
            True if the URL is allowed by robots.txt

        Raises:
            TypeError: If resource is not a string, Url, or Resource
            RobotDisallowedError: If the URL is disallowed by robots.txt

        Example:
            >>> if robot.can_fetch("https://example.com/page"):
            ...     response = client.get(Resource("https://example.com/page"))
        """
        # this is an ingress point, so we should be able to handle Url or str; but normalise to Resource
        if isinstance(resource, (str, Url)):
            resource = Resource(Url(resource))
        if not isinstance(resource, Resource):
            raise TypeError(
                f"Expected string, Url, or Resource, got {type(resource).__name__}"
            )

        # Use provided User-Agent or fall back to client's default or system default.
        if user_agent is None:  # Only if no user agent provided
            if hasattr(self._context.client, "user_agent"):  # Try client's user agent
                user_agent = (
                    self._context.client.user_agent  # pyright: ignore[reportAttributeAccessIssue]
                )
            else:  # Fall back to config
                user_agent = Config().http.user_agent

        can_fetch = self._parser.can_fetch(str(resource.url), user_agent)

        # Log the decision with the used User-Agent for better debugging
        if can_fetch:
            self._logger.debug(
                "Permission check for %s with User-Agent '%s': allowed",
                resource.url,
                user_agent,
            )
        else:
            self._logger.warning(
                "Permission check for %s with User-Agent '%s': denied",
                resource.url,
                user_agent,
            )
            raise RobotDisallowedError(
                f"Permission denied by robots.txt for {resource.url} with User-Agent '{user_agent}'",
            )

        return can_fetch

    @property
    def sitemaps(self) -> ResourceList:
        """Get sitemap URLs referenced in robots.txt.

        Returns:
            ResourceList containing IndexEntry objects for each sitemap URL

        Example:
            >>> for sitemap in robot.sitemaps:
            ...     print(f"Found sitemap: {sitemap.url}")
        """
        # Convert iterator to list first
        sitemap_urls = list(self._parser.sitemaps)

        self._logger.debug("Retrieving %d sitemaps from robots.txt", len(sitemap_urls))

        sitemaps: ResourceList = ResourceList()
        for sitemap in sitemap_urls:
            sitemaps.append(IndexEntry(Url(sitemap)))

        return sitemaps
