from functools import wraps
from socket import gaierror, gethostbyname
from typing import Any, Union
from urllib import parse


def http_only(func):
    """
    Decorator to restrict property access to HTTP/HTTPS URLs only.

    This decorator ensures that the decorated method is only called if the URL scheme
    is either 'http' or 'https'. If the URL scheme is not 'http' or 'https', a ValueError
    is raised.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The wrapped function that includes the URL scheme check.

    Raises:
        ValueError: If the URL scheme is not 'http' or 'https'.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._parsed.scheme not in ["http", "https"]:
            raise ValueError("Only valid for HTTP and HTTPS urls")
        return func(self, *args, **kwargs)

    return wrapper


# TODO: think about how to handle username and passwords
# We do need access to the password presumeably in some contexts; but also want to make sure it gets masked in stdout / logs


class Url:
    """
    URL handling and parsing.

    A utility class for manipulating and parsing URLs, ensuring they're properly
    formatted and providing easy access to their components. Supports HTTP, HTTPS,
    and file URLs with different behavior for each scheme.

    Examples:
        >>> from ethicrawl import Url
        >>> url = Url("https://example.com/path?q=search")
        >>> print(url.netloc)
        example.com
        >>> print(url.path)
        /path
        >>> print(url.query_params)
        {'q': 'search'}

        # Extending URLs
        >>> url = Url("https://example.com")
        >>> new_url = url.extend("products")
        >>> print(new_url)
        https://example.com/products

        # Adding query parameters
        >>> url = Url("https://example.com/search")
        >>> new_url = url.extend({"q": "term", "page": "1"})
        >>> print(new_url)
        https://example.com/search?q=term&page=1

    Attributes:
        scheme (str): URL scheme (http, https, file)
        netloc (str): Network location/domain (HTTP/HTTPS only)
        hostname (str): Just the hostname part without port (HTTP/HTTPS only)
        path (str): URL path
        params (str): URL parameters (semicolon params, HTTP/HTTPS only)
        query (str): Raw query string (HTTP/HTTPS only)
        query_params (dict): Query parameters as a dictionary (HTTP/HTTPS only)
        fragment (str): URL fragment/anchor (HTTP/HTTPS only)
        base (str): Base URL (scheme + netloc for HTTP/HTTPS, 'file://' for file)
    """

    def __init__(self, url: Union[str, "Url"], validate: bool = False):
        """
        Initialize a URL object.

        Args:
            url (str or Url): URL string or another Url object
            validate (bool): If True, performs hostname resolution to validate
                            the domain (HTTP/HTTPS only)

        Raises:
            ValueError: If URL is invalid or hostname can't be resolved (when validate=True)
        """
        if isinstance(url, Url):
            url = str(url)

        self._parsed = parse.urlparse(url)

        # Basic validation
        if self._parsed.scheme not in ["file", "http", "https"]:
            raise ValueError(f"Only File and HTTP(S) URLs supported: {url}")

        # For HTTP/HTTPS URLs, ensure netloc exists
        if self._parsed.scheme in ["http", "https"] and not self._parsed.netloc:
            raise ValueError(f"Invalid HTTP URL (missing domain): {url}")

        # For file URLs, ensure path exists
        if self._parsed.scheme == "file" and not self._parsed.path:
            raise ValueError(f"Invalid file URL (missing path): {url}")

        # Domain resolution validation (for HTTP/HTTPS only)
        if validate and self._parsed.scheme in ["http", "https"]:
            try:
                gethostbyname(str(self._parsed.hostname))
            except gaierror:
                raise ValueError(
                    f"Cannot resolve hostname: {self._parsed.hostname}")

    @property
    def base(self) -> str:
        """Get scheme and netloc."""
        if self.scheme == "file":
            return "file://"
        return f"{self.scheme}://{self.netloc}"

    @property
    def scheme(self) -> str:
        """Get the URL scheme (file, http or https)."""
        return self._parsed.scheme

    @property
    @http_only
    def netloc(self) -> str:
        """Get the network location (domain)."""
        return self._parsed.netloc

    @property
    @http_only
    def hostname(self) -> str:
        """Get just the hostname part."""
        return str(self._parsed.hostname)

    @property
    def path(self) -> str:
        """Get the path component."""
        return self._parsed.path

    @property
    @http_only
    def params(self) -> str:
        """Get URL parameters."""
        return self._parsed.params

    @property
    @http_only
    def query(self) -> str:
        """Get the query string."""
        return self._parsed.query

    @property
    @http_only
    def query_params(self) -> dict[str, Any]:
        """
        Get parsed query parameters as a dictionary.

        Parses the URL's query string into a dictionary of parameter name/value pairs.
        Only available for HTTP/HTTPS URLs.

        Returns:
            dict: Dictionary of query parameters

        Raises:
            ValueError: If used on a file:// URL
        """
        return dict(parse.parse_qsl(self._parsed.query))

    @property
    @http_only
    def fragment(self) -> str:
        """Get URL fragment."""
        return self._parsed.fragment

    def __str__(self) -> str:
        """String representation of the URL."""
        return self._parsed.geturl()

    def __eq__(self, other):
        """Compare URLs for equality."""
        if isinstance(other, Url):
            return str(self) == str(other)
        elif isinstance(other, str):
            return str(self) == other
        return False

    def __hash__(self):
        """Hash implementation for using URLs in sets/dicts."""
        return hash(str(self))

    @http_only
    def _extend_with_params(self, params: dict[str, Any]) -> "Url":
        """Add query parameters to URL."""
        current_params = self.query_params
        current_params.update(params)

        query_string = parse.urlencode(current_params)

        # Create new URL with updated query string
        base_url = f"{self.scheme}://{self.netloc}{self.path}"
        if self._parsed.params:
            base_url += f";{self._parsed.params}"

        # Add fragment if it exists
        fragment = f"#{self._parsed.fragment}" if self._parsed.fragment else ""

        return Url(
            f"{base_url}?{query_string}{fragment}"
            if query_string
            else f"{base_url}{fragment}"
        )

    def _extend_with_path(self, path: str) -> "Url":
        """Add path component to URL."""
        # Set location based on scheme
        if self.scheme == "file":
            loc = ""  # Empty for file URLs
        else:
            loc = self.netloc  # Use netloc for HTTP(S)

        # Handle path joining logic uniformly
        if path.startswith("/"):
            # Path has leading slash
            if self.path.endswith("/"):
                # Remove duplicate slash if base path ends with slash
                new_path = self.path + path[1:]
            else:
                # Keep the leading slash
                new_path = self.path + path
        else:
            # No leading slash in path
            if not self.path:
                new_path = "/" + path
            elif self.path.endswith("/"):
                new_path = self.path + path
            else:
                new_path = self.path + "/" + path

        # Unified URL construction
        return Url(f"{self.scheme}://{loc}{new_path}")

    def extend(self, *args, **kwargs) -> "Url":
        """
        Extend the URL with path components or query parameters.

        This method allows flexible extension of URLs in different ways:

        1. Add path component: extend("path/to/resource")
        2. Add query parameters as dictionary: extend({"param1": "value1"})
        3. Add single query parameter: extend("param_name", "param_value")

        Note that query parameter operations are only available for HTTP/HTTPS URLs,
        not for file URLs.

        Args:
            *args: Either a path string, a parameter dictionary, or a name/value pair

        Returns:
            Url: A new Url instance with the extensions applied

        Raises:
            ValueError: For invalid arguments or when trying to add query parameters to file URLs

        Examples:
            >>> url = Url("https://example.com")
            >>> # Add path
            >>> url.extend("products").extend("category")
            'https://example.com/products/category'
            >>> # Add parameters
            >>> url.extend({"search": "term", "page": "1"})
            'https://example.com?search=term&page=1'
        """
        # Case 1: Dictionary of parameters
        if (
            self.scheme in ["http", "https"]
            and len(args) == 1
            and isinstance(args[0], dict)
        ):
            params = args[0]
            return self._extend_with_params(params)

        # Case 2: Key-value parameter pair
        elif self.scheme in ["http", "https"] and len(args) == 2:
            param_name, param_value = args
            return self._extend_with_params({param_name: param_value})

        # Case 3: Path component (works for all schemes)
        elif len(args) == 1 and isinstance(args[0], str):
            path_component = args[0]
            return self._extend_with_path(path_component)

        # Invalid usage
        else:
            if self.scheme == "file" and (
                len(args) == 1 and isinstance(args[0], dict) or len(args) == 2
            ):
                raise ValueError(
                    "Query parameters are not supported for file:// URLs")
            raise ValueError("Invalid arguments for extend()")
