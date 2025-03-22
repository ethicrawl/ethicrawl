import requests

from ethicrawl.client.transport import Transport
from ethicrawl.config import Config
from ethicrawl.context import Context
from ethicrawl.core import Headers, Url

from .http_request import HttpRequest
from .http_response import HttpResponse


class RequestsTransport(Transport):
    """Transport implementation using the requests library."""

    def __init__(self, context: Context):
        self._context = context
        self._logger = self._context.logger("client.requests")
        self.session = requests.Session()
        self._default_user_agent = Config().http.user_agent
        self.session.headers.update({"User-Agent": self._default_user_agent})

    @property
    def user_agent(self) -> str:
        """
        Get the User-Agent string used by requests.

        Returns:
            str: The User-Agent string
        """
        return str(self.session.headers.get("User-Agent", self._default_user_agent))

    @user_agent.setter
    def user_agent(self, agent: str):
        """
        Set the User-Agent string for requests.

        Args:
            agent (str): The User-Agent string to use
        """
        self.session.headers.update({"User-Agent": agent})

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Make a GET request using requests library.

        Args:
            request (HttpRequest): The request to perform

        Returns:
            HttpResponse: Standardized response object
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
