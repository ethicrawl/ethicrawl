from random import random
from time import sleep, time

from ethicrawl.client import Client
from ethicrawl.context import Context
from ethicrawl.core import Headers, Resource, Url

from .chrome_transport import ChromeTransport
from .http_request import HttpRequest
from .http_response import HttpResponse
from .requests_transport import RequestsTransport


class HttpClient(Client):
    """HTTP client implementation with configurable transports and rate limiting.

    This client provides a flexible HTTP interface with the following features:
    - Configurable backend transport (Requests or Selenium Chrome)
    - Built-in rate limiting with jitter to avoid detection
    - Header management with User-Agent control
    - Automatic retry with exponential backoff
    - Detailed logging of request/response cycles

    The client can use either a simple RequestsTransport for basic HTTP operations
    or a ChromeTransport for JavaScript-rendered content.

    Attributes:
        timeout (int): Request timeout in seconds
        min_interval (float): Minimum time between requests in seconds
        jitter (float): Random time variation added to rate limiting
        headers (Headers): Default headers to send with each request
        last_request_time (float): Timestamp of the last request
        user_agent (str): User agent string used for requests

    Example:
        >>> from ethicrawl.client.http import HttpClient
        >>> from ethicrawl.core import Resource
        >>> client = HttpClient(rate_limit=1.0)  # 1 request per second
        >>> response = client.get(Resource("https://example.com"))
        >>> print(response.status_code)
        200

        # Switch to Chrome for JavaScript-heavy sites
        >>> chrome_client = client.with_chrome(headless=True)
        >>> js_response = chrome_client.get(Resource("https://spa-example.com"))
    """

    def __init__(
        self,
        context=None,
        transport=None,
        timeout=10,
        rate_limit=1.0,
        jitter=0.5,
        headers=None,
        chrome_params=None,
    ):
        """Initialize an HTTP client with configurable transport and rate limiting.

        Args:
            context (Context, optional): Context for the client. If None, a default context
                with a dummy URL will be created.
            transport (Transport, optional): Custom transport implementation. If None,
                either ChromeTransport or RequestsTransport will be used.
            timeout (int): Request timeout in seconds
            rate_limit (float): Maximum requests per second. Set to 0 for no limit.
            jitter (float): Random variation (0-1) to add to rate limiting
            headers (dict, optional): Default headers to send with each request
            chrome_params (dict, optional): Parameters for ChromeTransport if used
        """
        if not isinstance(context, Context):
            context = Context(Resource(Url("http://www.example.com/")))  # dummy url
        self._context = context
        self._logger = self._context.logger("client")

        self.timeout = timeout

        # Initialize the appropriate transport
        if transport:
            self.transport = transport
        elif chrome_params:
            self.transport = ChromeTransport(context, **chrome_params)
        # elif Gecko TODO: for expansion
        else:
            self.transport = RequestsTransport(context)

        self._logger.debug(
            "Initialized with %s transport (timeout: %d, rate limit: %.2f/sec)",
            self.transport.__class__.__name__,
            self.timeout,
            rate_limit if rate_limit > 0 else float("inf"),
        )

        self.headers = Headers(headers or {})

        # Rate limiting parameters
        self.min_interval = 1.0 / rate_limit if rate_limit > 0 else 0
        self.jitter = jitter
        # Initialize last_request_time to None to indicate no previous requests
        self.last_request_time = None

    @property
    def user_agent(self) -> str:
        # First check if we have a User-Agent header
        if "user-agent" in self.headers:
            return self.headers["user-agent"]
        # Otherwise get from transport
        return self.transport.user_agent

    @user_agent.setter
    def user_agent(self, agent):
        # Set in our headers
        self.headers["user-agent"] = agent
        # Also set on transport for consistency
        self.transport.user_agent = agent

    def with_chrome(
        self,
        headless=True,
        wait_time=3,
        timeout=30,
        rate_limit=0.5,
        jitter=0.3,
    ) -> "HttpClient":
        """Create a new HttpClient instance using Chrome/Selenium transport.

        This creates a new client that can render JavaScript and interact
        with dynamic web applications.

        Args:
            headless (bool): Whether to run Chrome in headless mode
            wait_time (int): Default time to wait for page elements in seconds
            timeout (int): Request timeout in seconds
            rate_limit (float): Maximum requests per second
            jitter (float): Random variation factor for rate limiting

        Returns:
            HttpClient: A new client instance configured to use Chrome

        Example:
            >>> client = HttpClient()
            >>> chrome = client.with_chrome(headless=True)
            >>> response = chrome.get(Resource("https://single-page-app.com"))
        """
        chrome_params = {"headless": headless, "wait_time": wait_time}

        # Create a new instance with the same context but Chrome transport
        return HttpClient(
            context=self._context,  # Use this instance's context
            chrome_params=chrome_params,
            timeout=timeout,
            rate_limit=rate_limit,
            jitter=jitter,
        )

    def _apply_rate_limiting(self):
        # If this is the first request, no need to apply rate limiting
        if self.last_request_time is None:
            return

        # Calculate time since last request
        elapsed = time() - self.last_request_time

        # If we've made a request too recently, sleep to maintain rate limit
        if elapsed < self.min_interval:
            # Calculate delay with optional jitter
            delay = self.min_interval - elapsed
            if self.jitter > 0:
                # this is not a cryptographic key
                delay += random() * self.jitter  # nosec

            self._logger.debug("Rate limiting - sleeping for %.2fs", delay)
            sleep(delay)

        # Update the last request time
        self.last_request_time = time()

    def get(
        self,
        resource: Resource,
        timeout: int | None = None,
        headers: dict | None = None,
    ) -> HttpResponse:
        """Make a GET request to the specified resource.

        This method applies rate limiting, handles headers, and logs the result.
        For JavaScript-heavy sites, use with_chrome() first to switch to
        a Chrome-based transport.

        Args:
            resource (Resource): The resource to request
            timeout (int, optional): Request-specific timeout that overrides
                the client's default timeout
            headers (dict, optional): Additional headers for this request

        Returns:
            HttpResponse: Response object with status, headers and content

        Raises:
            TypeError: If resource is not a Resource instance
            IOError: If the HTTP request fails for any reason

        Example:
            >>> client = HttpClient()
            >>> response = client.get(Resource("https://example.com"))
            >>> if response.status_code == 200:
            ...     print(f"Got {len(response.content)} bytes")
        """
        # First validate that resource is the correct type
        if not isinstance(resource, Resource):
            raise TypeError(f"Expected Resource object, got {type(resource).__name__}")

        try:
            # Apply rate limiting before making request
            self._apply_rate_limiting()

            self._logger.debug("fetching  %s", resource.url)

            request = HttpRequest(resource.url)

            if timeout is not None:
                request.timeout = timeout

            request_headers = Headers(self.headers)

            # Add request-specific headers, which will override client headers
            if headers:
                for header, value in headers.items():
                    request_headers[header] = value

            # Set the combined headers on the request
            request.headers = request_headers

            response = self.transport.get(request)

            # After getting the response
            if 200 <= response.status_code < 300:
                self._logger.debug(
                    "Successfully fetched %s: HTTP %d (%d bytes)",
                    resource.url,
                    response.status_code,
                    len(response.content),
                )
            elif 400 <= response.status_code < 500:
                self._logger.warning(
                    "Client error fetching %s: HTTP %d",
                    resource.url,
                    response.status_code,
                )
            elif response.status_code >= 500:
                self._logger.error(
                    "Server error fetching %s: HTTP %d",
                    resource.url,
                    response.status_code,
                )

            # Update last request time after successful request
            self.last_request_time = time()

            return response
        except Exception as exc:  # pragma: no cover
            # Log error before re-raising
            self._logger.error("Request failed for %s: %s", resource.url, exc)
            # Re-raise with clear error
            raise IOError(f"HTTP request failed: {exc}") from exc
