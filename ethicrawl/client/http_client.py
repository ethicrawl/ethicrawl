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
    HTTP client for making web requests with rate limiting and jitter.

    Supports both regular HTTP requests and Chromium-driven browser requests.
    This client automatically applies rate limiting and jitter to avoid
    overloading servers with requests.

    Examples:
        >>> from ethicrawl import HttpClient, Resource, Url
        >>> client = HttpClient(timeout=30, rate_limit=1.0, jitter=0.2)
        >>> url = Url("https://example.com")
        >>> resource = Resource(url)
        >>> response = client.get(resource)
        >>> print(response.status_code)
        200

    Attributes:
        transport: The underlying transport (RequestsTransport or ChromiumTransport)
        timeout (int): Default timeout for requests in seconds
        user_agent (str): User agent string used for requests
        min_interval (float): Minimum time between requests in seconds
        jitter (float): Random delay factor (0-1) for rate limiting
    """

    def __init__(
        self,
        context=None,
        transport=None,
        timeout=10,
        rate_limit=1,
        jitter=0.5,
        chromium_params=None,
    ):
        """
        Initialize the HTTP client.

        Args:
            context (Context, optional): Context for the client. If None, a default
                                       Context with a dummy URL will be created.
            transport (Transport, optional): Transport implementation to use.
                                          If None, RequestsTransport is used.
            timeout (int): Request timeout in seconds
            rate_limit (float): Maximum requests per second (0 for unlimited)
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
        self.last_request_time = None  # Initialize last_request_time to None to indicate no previous requests

    @property
    def user_agent(self):
        """
        Get the User-Agent from the underlying transport.

        Returns:
            str: The current User-Agent string
        """
        return self.transport.user_agent

    @user_agent.setter
    def user_agent(self, agent):
        """
        Set the User-Agent on the underlying transport.

        Args:
            agent (str): The User-Agent string to use for requests
        """
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
        Create a new client that uses a Chromium-powered transport.

        Creates a new HttpClient instance that uses Selenium with Chrome/Chromium to execute
        JavaScript and render pages before returning them, allowing extraction
        of content from modern single-page applications.

        Args:
            headless (bool): Run browser in headless mode
            wait_time (int): Wait time for JavaScript execution in seconds
            timeout (int): Request timeout in seconds
            rate_limit (float): Maximum requests per second
            jitter (float): Random delay factor (0-1)

        Returns:
            HttpClient: A new client configured with Chromium transport

        Example:
            >>> from ethicrawl import HttpClient
            >>> client = HttpClient()
            >>> chromium_client = client.with_chromium(headless=False)
            >>> # Now use chromium_client for JavaScript-heavy pages
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
        """Apply rate limiting to avoid overloading servers."""
        # If this is the first request, no need to apply rate limiting
        if self.last_request_time is None:
            return

        # Calculate time since last request
        elapsed = time.time() - self.last_request_time

        # If we've made a request too recently, sleep to maintain rate limit
        if elapsed < self.min_interval:
            # Calculate delay with optional jitter
            delay = self.min_interval - elapsed
            if self.jitter > 0:
                # this is not a cryptographic key
                delay += random.random() * self.jitter  # nosec

            self._logger.debug(f"Rate limiting - sleeping for {delay:.2f}s")
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
            timeout (int, optional): Request timeout override for this request
            headers (dict, optional): Additional headers for this request

        Returns:
            HttpResponse: The response from the server

        Raises:
            IOError: If the request fails due to network issues or other errors
            TypeError: If resource is not a Resource object
        """
        # First validate that resource is the correct type
        if not isinstance(resource, Resource):
            raise TypeError(f"Expected Resource object, got {type(resource).__name__}")

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
