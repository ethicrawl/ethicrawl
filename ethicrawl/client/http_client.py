import time
import random
from .requests_transport import RequestsTransport
from .chromium_transport import ChromiumTransport
from ethicrawl.core.ethicrawl_context import EthicrawlContext


class HttpClient:
    """
    A simple HTTP client for making web requests with rate limiting and jitter.
    Supports both regular HTTP requests and Chromium-driven browser requests.
    """

    def __init__(
        self,
        transport=None,
        timeout=10,
        rate_limit=1,
        jitter=0.5,
        chromium_params=None,
    ):
        """
        Initialize the HTTP client.

        Args:
            transport (Transport, optional): Transport implementation to use
            timeout (int): Request timeout in seconds
            rate_limit (float): Maximum requests per second
            jitter (float): Random delay factor (0-1) to add to rate limiting
            chromium_params (dict, optional): Parameters for Chromium if used
                                            (headless, wait_time, chrome_driver_path)
        """
        self.context = None
        self.timeout = timeout

        # Initialize the appropriate transport
        if transport:
            self.transport = transport
        elif chromium_params:
            self.transport = ChromiumTransport(**chromium_params)
        # elif Gecko TODO: for expansion
        else:
            self.transport = RequestsTransport()

        self.headers = {}

        # Rate limiting parameters
        self.min_interval = 1.0 / rate_limit if rate_limit > 0 else 0
        self.jitter = jitter
        self.last_request_time = time.time()

    @property
    def user_agent(self):
        """Get the User-Agent from the underlying transport."""
        return self.transport.user_agent

    @user_agent.setter
    def user_agent(self, agent):
        """Set the User-Agent on the underlying transport."""
        self.transport.user_agent = agent

    @classmethod
    def with_chromium(
        cls,
        headless=True,
        wait_time=3,
        timeout=30,
        rate_limit=0.5,
        jitter=0.3,
    ):
        """
        Factory method to create a Chromium-powered HTTP client.

        Args:
            headless (bool): Run in headless mode
            wait_time (int): Wait time for JavaScript execution
            chrome_driver_path (str, optional): Path to chromedriver
            timeout (int): Request timeout
            rate_limit (float): Requests per second
            jitter (float): Random delay factor

        Returns:
            HttpClient: Configured with Chromium transport
        """
        chromium_params = {"headless": headless, "wait_time": wait_time}

        return cls(
            chromium_params=chromium_params,
            timeout=timeout,
            rate_limit=rate_limit,
            jitter=jitter,
        )

    def _apply_rate_limiting(self):
        """Apply rate limiting with jitter before making a request."""
        if self.min_interval <= 0:
            return

        # Calculate time since last request
        now = time.time()
        elapsed = now - self.last_request_time

        # Calculate delay needed to maintain rate limit
        delay = self.min_interval - elapsed

        # Add random jitter (0-100% of jitter value)
        jitter_amount = 0
        if delay > 0 and self.jitter > 0:
            jitter_amount = random.uniform(0, self.jitter * self.min_interval)
            delay += jitter_amount

        # Sleep if needed
        if delay > 0:
            time.sleep(delay)

        # Update the last request time
        self.last_request_time = time.time()

    def get(self, url):
        """
        Make a GET request to the specified URL with rate limiting.

        Args:
            url (str): The URL to request

        Returns:
            HttpResponse: The response from the server
        """
        try:
            # Apply rate limiting before making request
            self._apply_rate_limiting()

            response = self.transport.get(
                url, timeout=self.timeout, headers=self.headers
            )

            # Update last request time after successful request
            self.last_request_time = time.time()

            return response
        except Exception as e:
            # Re-raise with clear error
            raise IOError(f"HTTP request failed: {e}")
