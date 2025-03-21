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
        return self.session.headers.get("User-Agent", self._default_user_agent)

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
        try:
            url = str(request.url)

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

            # Make the request with merged headers
            if proxies:
                response = self.session.get(
                    url, timeout=timeout, headers=merged_headers, proxies=proxies
                )
            else:
                response = self.session.get(
                    url, timeout=timeout, headers=merged_headers
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
        except Exception as e:  # pragma: no cover
            raise IOError(f"Error fetching {url}: {e}")
