from .transport import Transport
from .http_response import HttpResponse
import requests


class RequestsTransport(Transport):
    """Transport implementation using the requests library."""

    def __init__(self):
        self.session = requests.Session()
        # Set a default User-Agent
        self._default_user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
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

    def get(self, url, timeout=None, headers=None) -> HttpResponse:
        """
        Make a GET request using requests library.

        Args:
            url (str): The URL to request
            timeout (int, optional): Request timeout in seconds
            headers (dict, optional): Additional headers

        Returns:
            HttpResponse: Standardized response object
        """
        try:
            if headers:
                self.session.headers.update(headers)

            response = self.session.get(url, timeout=timeout)

            # Convert requests.Response to our HttpResponse
            return HttpResponse(
                status_code=response.status_code,
                text=response.text,
                headers=dict(response.headers),
                content=response.content,
            )
        except Exception as e:
            raise IOError(f"Error fetching {url}: {e}")
