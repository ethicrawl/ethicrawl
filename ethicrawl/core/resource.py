from dataclasses import dataclass
from typing import Any

from .url import Url


@dataclass
class Resource:
    """URL-identified entity within the crawler system.

    Resource is a generic representation of anything addressable by a URL
    within the Ethicrawl system. It serves as a common foundation for various
    components like requests, responses, robots.txt files, sitemap entries, etc.

    This class provides URL type safety, consistent equality comparison, and
    proper hashing behavior for all URL-addressable entities.

    Attributes:
        url: The Url object identifying this resource. Can be initialized
            with either a string or Url object.

    Raises:
        TypeError: When initialized with something other than a string or Url object

    Examples:
        >>> resource = Resource("https://example.com/robots.txt")
        >>> resource.url.path
        '/robots.txt'
        >>> resource2 = Resource(Url("https://example.com/robots.txt"))
        >>> resource == resource2
        True
    """

    url: Url

    def __post_init__(self):
        """Validate and normalize the url attribute after initialization.

        Converts string URLs to Url objects and raises TypeError for invalid types.
        """
        if isinstance(self.url, str):  # user provided a str; cast to Url
            self.url = Url(self.url)
        if not isinstance(self.url, Url):
            raise TypeError(
                f"Error creating resource, got {type(self.url).__name__} expected str or Url"
            )

    def __hash__(self) -> int:
        """Generate a hash based on the string representation of the URL.

        Returns:
            Integer hash value
        """
        return hash(str(self.url))

    def __eq__(self, other: Any) -> bool:
        """Compare resources for equality based on their URLs.

        Two resources are considered equal if they have the same URL.

        Args:
            other: Another Resource object to compare with

        Returns:
            True if resources have the same URL, False otherwise
        """
        if not isinstance(other, self.__class__):
            return False
        return str(self.url) == str(other.url)

    def __str__(self) -> str:
        """Return the URL as a string for better readability."""
        return str(self.url)

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"Resource('{self.url}')"
