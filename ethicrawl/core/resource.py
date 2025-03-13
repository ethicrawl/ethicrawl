from dataclasses import dataclass
from ethicrawl.core.url import Url


@dataclass
class Resource:
    """
    Resource abstraction for web content.

    Represents a web resource with its URL. Used as the primary object for
    passing URLs through the system with context.

    Examples:
        >>> from ethicrawl import Resource, Url
        >>> resource = Resource(Url("https://example.com/image.jpg"))
        >>> print(resource.url.path)
        /image.jpg

        # String URLs are automatically converted to Url objects
        >>> resource = Resource("https://example.com/image.jpg")
        >>> isinstance(resource.url, Url)
        True

        # Resources can be used in sets and as dictionary keys
        >>> resources = {Resource("https://example.com/a"), Resource("https://example.com/b")}
        >>> len(resources)
        2

    Attributes:
        url (Url): The URL of the resource. Can be provided as a string or Url object.
    """

    url: Url

    def __post_init__(self):
        """
        Validate and normalize the URL.

        Automatically converts string URLs to Url objects.

        Raises:
            ValueError: If url is neither a string nor a Url object
        """
        if isinstance(self.url, str):  # user provided a str; cast to Url
            self.url = Url(self.url)
        if not isinstance(self.url, Url):
            raise ValueError(
                f"Error creating resource, got type {type(self.url)} expected str or Url"
            )

    def __hash__(self):
        """
        Make instances hashable based on their URL.

        This allows Resource objects to be used in sets or as dictionary keys.

        Returns:
            int: Hash value based on the string representation of the URL
        """
        return hash(str(self.url))

    def __eq__(self, other):
        """
        Equality check based on URL and exact type.

        Two Resource objects are considered equal if they're of the same class
        and have the same URL.

        Args:
            other: Object to compare with

        Returns:
            bool: True if objects are equal, False otherwise
        """
        if not isinstance(other, self.__class__):
            return False
        return str(self.url) == str(other.url)
