from protego import Protego
from ethicrawl.sitemaps.sitemap_entries import IndexEntry
from ethicrawl.core.context import Context
from ethicrawl.core.resource import Resource
from ethicrawl.core.url import Url
from ethicrawl.core.resource_list import ResourceList
from typing import Union


class RobotsHandler:
    """
    Handler for robots.txt processing and URL permission checking.

    This class encapsulates all robots.txt related functionality for a single domain.
    """

    def __init__(self, context: Context) -> None:
        """
        Initialize the RobotsHandler for a specific domain.

        Args:
            http_client: HTTP client for fetching robots.txt files
            base_url (str): Base URL of the domain to handle
            logger: Logger for logging messages (optional)
        """
        if not isinstance(context, Context):
            raise ValueError(f"Invalid Context Provided")
        else:
            self._context = context

        self._parser = None
        self._robots_status = None  # Track the HTTP status
        self._logger = self._context.logger("robots")

        # Initialize the parser immediately
        self._init_parser()

    def can_fetch(self, url_or_resource: Union[str, Url, Resource]) -> bool:
        """
        Check if a URL can be fetched according to robots.txt rules.

        Args:
            url_or_resource (str, Url, or Resource): URL to check permission for

        Returns:
            bool: True if allowed by robots.txt, False if disallowed

        Examples:
            >>> handler = RobotsHandler(context)
            >>> # All these are equivalent:
            >>> handler.can_fetch("https://example.com/page")
            >>> handler.can_fetch(Url("https://example.com/page"))
            >>> handler.can_fetch(Resource(Url("https://example.com/page")))
        """
        # Convert input to a Resource object
        if isinstance(url_or_resource, str):
            resource = Resource(Url(url_or_resource))
        elif isinstance(url_or_resource, Url):
            resource = Resource(url_or_resource)
        elif isinstance(url_or_resource, Resource):
            resource = url_or_resource
        else:
            raise TypeError(
                f"Expected string, Url, or Resource, got {type(url_or_resource)}"
            )

        # For 404, we explicitly allow everything per robots.txt protocol
        if self._robots_status == 404:
            self._logger.debug(
                f"Permission check for {resource.url}: allowed (no robots.txt)"
            )
            return True

        # For all other cases, use the parser
        can_fetch = self._parser.can_fetch(
            str(resource.url), self._context.client.user_agent
        )

        if can_fetch:
            self._logger.debug(f"Permission check for {resource.url}: allowed")
        else:
            self._logger.warning(f"Permission check for {resource.url}: denied")

        return can_fetch

    @property
    def sitemaps(self) -> ResourceList:
        """
        Get sitemap URLs from the robots.txt, resolving relative paths.

        Returns:
            list: List of SitemapIndexEntry objects
        """
        if not self._parser:
            return ResourceList()

        base_url = self._context.resource.url
        result = ResourceList([])

        for sitemap_url in self._parser.sitemaps:
            # Normalize the sitemap URL
            if sitemap_url.startswith("/"):
                # Relative to domain root
                absolute_url = f"{base_url.base}{sitemap_url}"
                self._logger.debug(
                    f"Resolved relative sitemap URL '{sitemap_url}' to '{absolute_url}'"
                )
                result.append(IndexEntry(absolute_url))
            elif not sitemap_url.startswith(("http://", "https://")):
                # No scheme, could be relative to current path
                absolute_url = f"{base_url.base}/{sitemap_url}"
                self._logger.debug(
                    f"Resolved relative sitemap URL '{sitemap_url}' to '{absolute_url}'"
                )
                result.append(IndexEntry(absolute_url))
            else:
                # Already absolute
                result.append(IndexEntry(sitemap_url))

        return result

    def _init_parser(self):
        """Initialize the robots.txt parser for the domain."""
        robots = Resource(f"{self._context.resource.url.base}/robots.txt")
        self._logger.info(f"Fetching robots.txt: {robots.url}")

        # Default to empty parser (permissive)
        self._parser = Protego.parse("")

        try:
            # Use our HTTP client to fetch robots.txt
            response = self._context.client.get(robots)

            # Store the status code directly without conversion
            self._robots_status = None
            if response:
                self._robots_status = response.status_code

            if response.status_code == 200:
                # Success - parse robots.txt normally
                self._parser = Protego.parse(response.text)
                self._logger.info(f"Successfully parsed {robots.url}")

                # Log sitemaps if present
                sitemaps = list(self._parser.sitemaps)
                if sitemaps:
                    self._logger.info(
                        f"Discovered {len(sitemaps)} sitemaps in {robots.url}"
                    )
                    for sitemap in sitemaps:
                        self._logger.debug(f"Discovered: {sitemap} in {robots.url}")
                else:
                    self._logger.info(f"No sitemaps found in {robots.url}")
            elif response.status_code == 404:
                # 404 - Standard is to allow everything
                self._logger.warning(
                    f"{robots.url} not found (404) - allowing all URLs"
                )
            elif response.status_code >= 400 and response.status_code != 404:
                # Other 4xx errors - Be conservative
                self._logger.warning(
                    f"{robots.url} returned {response.status_code} - being conservative"
                )
                self._parser = Protego.parse("User-agent: *\nDisallow: /")
            else:
                # Other unusual responses
                self._logger.warning(
                    f"{robots.url} returned{response.status_code} - being conservative"
                )
                self._parser = Protego.parse("User-agent: *\nDisallow: /")
        except Exception as e:
            self._logger.warning(f"Error fetching {robots.url}: {e}")
            # Exception during fetch - be conservative
            self._parser = Protego.parse("User-agent: *\nDisallow: /")
