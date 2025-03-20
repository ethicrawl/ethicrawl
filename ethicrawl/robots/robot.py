from dataclasses import dataclass

from protego import Protego

from ethicrawl.context import Context
from ethicrawl.core import Resource, ResourceList, Url
from ethicrawl.error import RobotDisallowedError
from ethicrawl.sitemaps import IndexEntry


@dataclass
class Robot(Resource):
    _context: (
        Context  # Do not change this after initialisation as stupid things will happen
    )

    def __post_init__(self):
        super().__post_init__()
        self._logger = self._context.logger("robots")
        response = self._context.client.get(Resource(self.url))
        if not hasattr(response, "status_code"):
            status_code = None
        else:
            status_code = response.status_code
        if status_code == 404:  # spec says fail open
            self._parser = Protego.parse("")
            self._logger.info(f"Server returned {status_code} - allowing all")
        elif status_code == 200:  # there's a robots.txt to use
            self._parser = Protego.parse(response.text)
            self._logger.info(
                f"Server returned {status_code} - using robots.txt")
        else:
            self._parser = Protego.parse("User-agent: *\nDisallow: /")
            self._logger.warning(
                f"Server returned {status_code} - denying all")

    @property
    def context(self) -> Context:
        return self._context

    def can_fetch(
        self, resource: Resource | Url | str, user_agent: str | None = None
    ) -> bool:
        """
        Check if a URL can be fetched according to robots.txt rules.

        Args:
            resource: URL to check (as str, Url, or Resource)
            user_agent: Optional User-Agent to check permissions for.
                       If None, uses the client's default User-Agent.

        Returns:
            bool: True if allowed by robots.txt

        Raises:
            RobotDisallowedError: If the URL is disallowed by robots.txt
            TypeError: If resource is not a string, Url, or Resource
        """
        # this is an ingress point, so we should be able to handle Url or str; but normalise to Resource
        if isinstance(resource, (str, Url)):
            resource = Resource(Url(resource))
        if not isinstance(resource, Resource):
            raise TypeError(
                f"Expected string, Url, or Resource, got {type(resource).__name__}"
            )

        # Use provided User-Agent or fall back to client's default
        if user_agent is None:
            user_agent = self._context.client.user_agent

        can_fetch = self._parser.can_fetch(str(resource.url), user_agent)

        # Log the decision with the used User-Agent for better debugging
        if can_fetch:
            self._logger.debug(
                f"Permission check for {resource.url} with User-Agent '{user_agent}': allowed"
            )
        else:
            self._logger.warning(
                f"Permission check for {resource.url} with User-Agent '{user_agent}': denied"
            )
            raise RobotDisallowedError(
                f"Permission denied by robots.txt for User-Agent '{user_agent}' at URL '{resource.url}'"
            )

        return can_fetch

    @property
    def sitemaps(self) -> ResourceList:
        sitemaps = ResourceList()
        for sitemap in self._parser.sitemaps:
            sitemaps.append(IndexEntry(Url(sitemap)))
        return sitemaps
