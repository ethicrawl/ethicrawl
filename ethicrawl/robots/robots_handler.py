from protego import Protego
from typing import List
from ethicrawl.sitemaps.sitemap_entries import IndexEntry
from ethicrawl.core.context import Context
from ethicrawl.core.resource import Resource
from ethicrawl.core.url import Url


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

        # self._http_client = http_client
        # self._base_url = base_url
        self._parser = None
        self._logger = self._context.logger("robots")

        # Initialize the parser immediately
        self._init_parser()

    def can_fetch(self, url: Resource):
        """
        Check if a URL can be fetched according to robots.txt rules.

        Args:
            url (str): URL to check

        Returns:
            bool: True if the URL can be fetched, False otherwise
        """
        can_fetch = self._parser.can_fetch(url, self._context.client.user_agent)
        self._logger.debug(
            f"Permission check for {url}: {'allowed' if can_fetch else 'denied'}"
        )
        return can_fetch

    @property
    def sitemaps(self) -> List[IndexEntry]:
        """
        Get sitemap URLs from the robots.txt, resolving relative paths.

        Returns:
            list: List of SitemapIndexEntry objects
        """
        if not self._parser:
            return []

        base_url = self._context.resource.url
        result = []

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
        """
        Initialize the robots.txt parser for the domain.
        """
        robots = Resource(f"{self._context.resource.url.base}/robots.txt")
        self._logger.info(f"Fetching robots.txt: {robots.url}")

        self._parser = Protego.parse("")

        try:
            # Use our HTTP client to fetch robots.txt
            response = self._context.client.get(robots)

            if response and response.status_code == 200:
                # Parse the robots.txt content using Protego
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
            else:
                self._logger.warning(f"{robots.url} not found")
        except Exception as e:
            msg = f"Error fetching {robots.url}: {e}"
            self._logger.warning(msg)
