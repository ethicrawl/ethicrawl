from .transport import Transport
from .http_response import HttpResponse
from ethicrawl.core.context import Context
import requests
from ethicrawl.config.config import Config
from ethicrawl.client.http_request import HttpRequest


class RequestsTransport(Transport):
    """Transport implementation using the requests library."""

    def __init__(self, context: Context):
        self.session = requests.Session()
        self._default_user_agent = Config().http.user_agent
        self.session.headers.update({"User-Agent": self._default_user_agent})

    @property
    def user_agent(self):
        """
        Get the User-Agent string used by requests.

        Returns:
            str: The User-Agent string
        """
        return self.session.headers.get("User-Agent", self._default_user_agent)

    @user_agent.setter
    def user_agent(self, agent):
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

            merged_headers = dict(self.session.headers)

            # Merge in request-specific headers (without modifying session)
            if request.headers:
                merged_headers.update(request.headers)

            # Prepare request kwargs
            kwargs = {"timeout": timeout, "headers": merged_headers}

            # Apply proxies at request level, avoiding environmental proxy issues
            if hasattr(Config().http, "proxies") and Config().http.proxies:
                kwargs["proxies"] = Config().http.proxies

            # Make the request with merged headers
            response = self.session.get(url, **kwargs)

            # Convert requests.Response to our HttpResponse
            return HttpResponse(
                status_code=response.status_code,
                request=request,
                text=response.text,
                headers=dict(response.headers),
                content=response.content,
            )
        except Exception as e:
            raise IOError(f"Error fetching {url}: {e}")
