import requests

from ethicrawl.client.transport import Transport
from ethicrawl.config import Config
from ethicrawl.context import Context
from ethicrawl.core import Headers, Url

from .http_request import HttpRequest
from .http_response import HttpResponse


class RequestsTransport(Transport):
    """HTTP transport implementation using the 'requests' library.

    This transport implementation handles HTTP requests using Python's requests
    library. It manages the underlying session, handles header management,
    proxy configuration, and converts between requests.Response objects and
    Ethicrawl's HttpResponse objects.

    The transport automatically applies configuration settings from the global
    Config object, including user agent, proxies, and default headers.

    Attributes:
        session (requests.Session): The underlying requests Session object
        user_agent (str): User agent string used for requests

    Example:
        >>> from ethicrawl.context import Context
        >>> from ethicrawl.client.http import RequestsTransport, HttpRequest
        >>> from ethicrawl.core import Resource
        >>> context = Context(Resource("https://example.com"))
        >>> transport = RequestsTransport(context)
        >>> transport.user_agent = "EthiCrawl/1.0"
        >>> request = HttpRequest(Resource("https://example.com/page"))
        >>> response = transport.get(request)
        >>> print(response.status_code)
        200
    """

    def __init__(self, context: Context):
        """Initialize the requests transport with a context.

        Sets up the requests.Session object with default headers from config.

        Args:
            context: The context to use for logging and resource resolution
        """
        self._context = context
        self._logger = self._context.logger("client.requests")
        self.session = requests.Session()
        self._default_user_agent = Config().http.user_agent
        self.session.headers.update({"User-Agent": self._default_user_agent})

    @property
    def user_agent(self) -> str:
        """Get the current user agent string.

        Returns:
            The user agent string currently set in session headers
        """
        return str(self.session.headers.get("User-Agent", self._default_user_agent))

    @user_agent.setter
    def user_agent(self, agent: str):
        """Set a new user agent string.

        Args:
            agent: New user agent string to use for requests
        """
        self.session.headers.update({"User-Agent": agent})

    def get(self, request: HttpRequest) -> HttpResponse:
        """Make a GET request using the requests library.

        Handles header merging, proxy configuration, and logging. Converts
        the requests.Response object to an HttpResponse.

        Args:
            request: The HttpRequest object containing URL, headers, etc.

        Returns:
            HttpResponse object with status, content, and headers

        Raises:
            IOError: If the request fails for any reason (wraps underlying exceptions)

        Example:
            >>> request = HttpRequest(Resource("https://example.com"))
            >>> request.headers["Accept"] = "text/html"
            >>> response = transport.get(request)
            >>> if response.status_code == 200:
            ...     print(f"Got {len(response.content)} bytes")
        """
        url = ""
        try:
            url = str(request.url)
            self._logger.debug("Making GET request to %s", url)

            timeout = request.timeout

            merged_headers = Headers(self.session.headers)

            # Merge in request-specific headers (without modifying session)
            if request.headers:
                merged_headers.update(request.headers)

            proxies = {}
            if Config().http.proxies.http:
                proxies["http"] = str(Config().http.proxies.http)
            if Config().http.proxies.https:
                proxies["https"] = str(Config().http.proxies.https)

            if proxies:
                response = self.session.get(
                    url, timeout=timeout, headers=merged_headers, proxies=proxies
                )
            else:
                response = self.session.get(
                    url, timeout=timeout, headers=merged_headers
                )

            # Log response info
            self._logger.debug(
                "Received response from %s: HTTP %s, %s bytes",
                url,
                response.status_code,
                len(response.content),
            )

            # Log non-success status codes at appropriate level
            if 400 <= response.status_code < 500:
                self._logger.warning(
                    "Client error: HTTP %s for %s", response.status_code, url
                )
            elif response.status_code >= 500:
                self._logger.error(
                    "Server error: HTTP %s for %s", response.status_code, url
                )

            # Convert requests.Response to our HttpResponse
            return HttpResponse(
                url=Url(response.url) or Url(request.url),
                status_code=response.status_code,
                request=request,
                text=response.text,
                headers=Headers(response.headers),
                content=response.content,
            )
        except Exception as exc:  # pragma: no cover
            self._logger.error("Failed to fetch %s: %s", url, exc)
            raise IOError(f"Error fetching {url}: {exc}") from exc
