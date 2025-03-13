import time
import random
from .requests_transport import RequestsTransport
from .chromium_transport import ChromiumTransport
from ethicrawl.core.context import Context
from ethicrawl.core.url import Url
from ethicrawl.core.resource import Resource
from ethicrawl.client.http_request import HttpRequest
from ethicrawl.client.http_response import HttpResponse


class HttpClient:
    """
    A simple HTTP client for making web requests with rate limiting and jitter.
    Supports both regular HTTP requests and Chromium-driven browser requests.
    """

    def __init__(
        self,
        context=Context,
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
        if not isinstance(context, Context):
            context = Context(Resource(Url("http://www.example.com/")))  # dummy url
        self._context = context
        self._logger = self._context.logger("client")

        self.timeout = timeout

        # Initialize the appropriate transport
        if transport:
            self.transport = transport
        elif chromium_params:
            self.transport = ChromiumTransport(context, **chromium_params)
        # elif Gecko TODO: for expansion
        else:
            self.transport = RequestsTransport(context)

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

    def with_chromium(
        self,
        headless=True,
        wait_time=3,
        timeout=30,
        rate_limit=0.5,
        jitter=0.3,
    ):
        """
        Convert this client to use a Chromium-powered transport.

        Args:
            headless (bool): Run in headless mode
            wait_time (int): Wait time for JavaScript execution
            timeout (int): Request timeout
            rate_limit (float): Requests per second
            jitter (float): Random delay factor

        Returns:
            HttpClient: A new client configured with Chromium transport
        """
        chromium_params = {"headless": headless, "wait_time": wait_time}

        # Create a new instance with the same context but Chromium transport
        return HttpClient(
            context=self._context,  # Use this instance's context
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

    def get(
        self, resource: Resource, timeout: int = None, headers: dict = None
    ) -> HttpResponse:
        """
        Make a GET request to the specified URL with rate limiting.

        Args:
            resource (Resource): The resource to request
            timeout (int, optional): Request timeout override
            headers (dict, optional): Additional headers for this request

        Returns:
            HttpResponse: The response from the server
        """
        try:
            # Apply rate limiting before making request
            self._apply_rate_limiting()

            self._logger.debug(f"fetching {resource.url}")

            request = HttpRequest(resource.url)

            if timeout is not None:
                request.timeout = timeout

            if headers:
                for header, value in headers.items():
                    request.headers[header] = value

            response = self.transport.get(request)

            # Update last request time after successful request
            self.last_request_time = time.time()

            return response
        except Exception as e:
            # Re-raise with clear error
            raise IOError(f"HTTP request failed: {e}")
