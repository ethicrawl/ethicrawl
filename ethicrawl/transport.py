from abc import ABC, abstractmethod


class Transport(ABC):
    """Abstract base class for HTTP transport implementations."""

    @abstractmethod
    def get(self, url, timeout=None, headers=None):
        """
        Make a GET request to the specified URL.

        Args:
            url (str): The URL to request
            timeout (int, optional): Request timeout in seconds
            headers (dict, optional): Additional headers

        Returns:
            Response: The response object
        """
        pass

    @property
    @abstractmethod
    def user_agent(self):
        """
        Get the User-Agent string used by this transport.

        Returns:
            str: The User-Agent string
        """
        pass

    @user_agent.setter
    @abstractmethod
    def user_agent(self, agent):
        """
        Set the User-Agent string for this transport.

        Args:
            agent (str): The User-Agent string to use
        """
        pass
