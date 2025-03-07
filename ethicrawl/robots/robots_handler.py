from protego import Protego
from typing import List
from ethicrawl.sitemaps.sitemap_urls import SitemapIndexUrl
from ethicrawl.core import EthicrawlContext


class RobotsHandler:
    """
    Handler for robots.txt processing and URL permission checking.

    This class encapsulates all robots.txt related functionality for a single domain.
    """

    def __init__(self, context: EthicrawlContext) -> None:
        """
        Initialize the RobotsHandler for a specific domain.

        Args:
            http_client: HTTP client for fetching robots.txt files
            base_url (str): Base URL of the domain to handle
            logger: Logger for logging messages (optional)
        """
        if not isinstance(context, EthicrawlContext):
            raise ValueError(f"Invalid Context Provided")
        else:
            self._context = context

        # self._http_client = http_client
        # self._base_url = base_url
        self._parser = None
        self._logger = self._context.logger("robots")

        # Initialize the parser immediately
        self._init_parser()

    def can_fetch(self, url):
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
    def sitemaps(self) -> List[SitemapIndexUrl]:
        """
        Get sitemap URLs from the robots.txt.

        Returns:
            list: List of sitemap URLs
        """
        if self._parser:

            return [SitemapIndexUrl(url) for url in self._parser.sitemaps]
            return list(self._parser.sitemaps)
        return []

    def _init_parser(self):
        """
        Initialize the robots.txt parser for the domain.
        """
        robots_url = f"{self._context.url}/robots.txt"
        self._logger.info(f"Fetching robots.txt: {robots_url}")

        self._parser = Protego.parse("")

        try:
            # Use our HTTP client to fetch robots.txt
            response = self._context.client.get(robots_url)

            if response and response.status_code == 200:
                # Parse the robots.txt content using Protego
                self._parser = Protego.parse(response.text)
                self._logger.info(f"Successfully parsed {robots_url}")

                # Log sitemaps if present
                sitemaps = list(self._parser.sitemaps)
                if sitemaps:
                    self._logger.info(
                        f"Discovered {len(sitemaps)} sitemaps in {robots_url}"
                    )
                    for sitemap in sitemaps:
                        self._logger.debug(f"Discovered: {sitemap} in {robots_url}")
                else:
                    self._logger.info(f"No sitemaps found in {robots_url}")
            else:
                self._logger.warning(f"{robots_url} not found")
        except Exception as e:
            msg = f"Error fetching {robots_url}: {e}"
            self._logger.warning(msg)
