from .http_client import HttpClient
from protego import Protego


class RobotsHandler:
    """
    Handler for robots.txt processing and URL permission checking.

    This class encapsulates all robots.txt related functionality for a single domain.
    """

    def __init__(self, http_client: HttpClient, base_url, logger=None) -> None:
        """
        Initialize the RobotsHandler for a specific domain.

        Args:
            http_client: HTTP client for fetching robots.txt files
            base_url (str): Base URL of the domain to handle
            logger: Logger for logging messages (optional)
        """
        self._http_client = http_client
        self._base_url = base_url
        self._parser = None

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
        print(self._http_client.user_agent)
        return self._parser.can_fetch(url, self._http_client.user_agent)

    def get_sitemaps(self):
        """
        Get sitemap URLs from the robots.txt.

        Returns:
            list: List of sitemap URLs
        """
        if self._parser:
            return list(self._parser.sitemaps)
        return []

    def _init_parser(self):
        """
        Initialize the robots.txt parser for the domain.
        """
        robots_url = f"{self._base_url}/robots.txt"
        print(f"Fetching robots.txt: {robots_url}")

        try:
            # Use our HTTP client to fetch robots.txt
            response = self._http_client.get(robots_url)

            if response and response.status_code == 200:
                # Parse the robots.txt content using Protego
                self._parser = Protego.parse(response.text)
                print(f"Successfully parsed robots.txt")

                # Log sitemaps if present
                sitemaps = list(self._parser.sitemaps)
                if sitemaps:
                    print(f"Found {len(sitemaps)} sitemaps in robots.txt")
                    for sitemap in sitemaps:
                        print(f"  - {sitemap}")
                else:
                    print("No sitemaps found in robots.txt")
            else:
                # If robots.txt can't be fetched, create an empty parser
                self._parser = Protego.parse("")
                print(f"No robots.txt found or couldn't be fetched")
        except Exception as e:
            # Create an empty parser on error
            self._parser = Protego.parse("")
            print(f"Error fetching robots.txt: {e}")
