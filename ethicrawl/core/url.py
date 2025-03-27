from functools import wraps
from socket import gaierror, gethostbyname
from typing import Any, Union
from urllib import parse

from ethicrawl.error import DomainResolutionError


def http_only(func):

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._parsed.scheme not in ["http", "https"]:
            raise ValueError("Only valid for HTTP and HTTPS urls")
        return func(self, *args, **kwargs)

    return wrapper


# TODO: think about how to handle username and passwords
# We do need access to the password presumeably in some contexts; but also want to make sure it gets masked in stdout / logs


class Url:
    """URL parser and manipulation class.

    This class provides methods for parsing, validating, and manipulating URLs.
    Supports HTTP, HTTPS, and file URL schemes with validation and component access.
    Path extension and query parameter manipulation are provided through the extend() method.

    Attributes:
        scheme: URL scheme (http, https, file)
        netloc: Network location/domain (HTTP/HTTPS only)
        hostname: Just the hostname portion of netloc (HTTP/HTTPS only)
        path: URL path component
        params: URL parameters (HTTP/HTTPS only)
        query: Raw query string (HTTP/HTTPS only)
        query_params: Query string parsed into a dictionary (HTTP/HTTPS only)
        fragment: URL fragment identifier (HTTP/HTTPS only)
        base: Base URL (scheme + netloc)

    Raises:
        ValueError: When provided with invalid URLs or when performing invalid operations
    """

    def __init__(self, url: Union[str, "Url"], validate: bool = False):
        """Initialize a URL object with parsing and optional validation.

        Args:
            url: String or Url object to parse
            validate: If True, performs additional validation including DNS resolution

        Raises:
            ValueError: When the URL has an invalid scheme or missing required components
            ValueError: When validate=True and the hostname cannot be resolved
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
            except gaierror as exc:
                # Raise a DomainResolutionError instead of ValueError
                raise DomainResolutionError(
                    str(self),  # Pass the full URL string
                    str(
                        self._parsed.hostname
                    ),  # Pass the hostname that failed resolution
                ) from exc

    @property
    def base(self) -> str:
        """Get the base URL (scheme and netloc).

        Returns:
            The base URL as a string (e.g., 'https://example.com')
        """
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
        """Get query parameters as a dictionary.

        Returns:
            Dictionary of query parameter keys and values

        Raises:
            ValueError: If called on a non-HTTP(S) URL
        """
        return dict(parse.parse_qsl(self._parsed.query))

    @property
    @http_only
    def fragment(self) -> str:
        """Get the fragment identifier from the URL.

        The fragment appears after # in a URL and typically
        references a section within a document.

        Returns:
            Fragment string without the # character

        Raises:
            ValueError: If called on a non-HTTP(S) URL
        """
        return self._parsed.fragment

    def __str__(self) -> str:
        """Convert URL to string representation.

        Returns:
            Complete URL string
        """
        return self._parsed.geturl()

    def __eq__(self, other: Any) -> bool:
        """Compare URLs for equality.

        Args:
            other: Another Url object or string to compare with

        Returns:
            True if URLs are equal, False otherwise
        """
        if isinstance(other, Url):
            return str(self) == str(other)
        elif isinstance(other, str):
            return str(self) == other
        return False

    def __hash__(self) -> int:
        """Return a hash of the URL.

        The hash is based on the string representation of the URL,
        ensuring URLs that are equal have the same hash.

        Returns:
            Integer hash value
        """
        return hash(str(self))

    @http_only
    def _extend_with_params(self, params: dict[str, Any]) -> "Url":
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

    def extend(self, *args: Any) -> "Url":
        """Extend the URL with additional path components or query parameters.

        This method supports multiple extension patterns:
        1. Path extension: extend("path/component")
        2. Single parameter: extend("param_name", "param_value")
        3. Multiple parameters: extend({"param1": "value1", "param2": "value2"})

        Args:
            *args: Either a path string, a parameter dict, or name/value parameter pair

        Returns:
            A new Url object with the extended path or parameters

        Raises:
            ValueError: If arguments don't match one of the supported patterns
            ValueError: If trying to add query parameters to a file:// URL

        Examples:
            >>> url = Url("https://example.com/api")
            >>> url.extend("v1").extend({"format": "json"})
            Url("https://example.com/api/v1?format=json")
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
                raise ValueError("Query parameters are not supported for file:// URLs")
            raise ValueError("Invalid arguments for extend()")
