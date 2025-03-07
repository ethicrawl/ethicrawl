import urllib.parse
import socket
from typing import Optional, Dict, Any, Union


class Url:
    """
    URL wrapper class with validation and utility methods.

    Provides typed URL handling, validation, and common operations
    to avoid passing raw strings around the codebase.
    """

    def __init__(self, url: Union[str, "Url"], validate: bool = False):
        """
        Initialize a new URL object.

        Args:
            url: A URL string or Url object to wrap
            validate: Whether to perform validation (domain resolution)

        Raises:
            ValueError: If the URL is invalid or domain can't be resolved
        """

        if isinstance(url, Url):
            url = str(url)

        self._parsed = urllib.parse.urlparse(url)

        # Basic validation
        if not self._parsed.scheme or not self._parsed.netloc:
            raise ValueError(f"Invalid URL: {url}")

        if self._parsed.scheme not in ["http", "https"]:
            raise ValueError(f"Only HTTP(S) URLs supported: {url}")

        # Domain resolution validation
        if validate:
            try:
                socket.gethostbyname(self._parsed.netloc)
            except socket.gaierror:
                raise ValueError(f"Cannot resolve hostname: {self._parsed.netloc}")

    @property
    def base(self) -> str:
        """Get scheme and netloc."""
        return f"{self.scheme}://{self.netloc}"

    @property
    def scheme(self) -> str:
        """Get the URL scheme (http or https)."""
        return self._parsed.scheme

    @property
    def netloc(self) -> str:
        """Get the network location (domain)."""
        return self._parsed.netloc

    @property
    def hostname(self) -> str:
        """Get just the hostname part."""
        return self._parsed.hostname

    @property
    def path(self) -> str:
        """Get the path component."""
        return self._parsed.path

    @property
    def params(self) -> str:
        """Get URL parameters."""
        return self._parsed.params

    @property
    def query(self) -> str:
        """Get the query string."""
        return self._parsed.query

    @property
    def query_params(self) -> Dict[str, Any]:
        """Get parsed query parameters as a dictionary."""
        return dict(urllib.parse.parse_qsl(self._parsed.query))

    @property
    def fragment(self) -> str:
        """Get URL fragment."""
        return self._parsed.fragment

    def extend(self, *args, **kwargs) -> "Url":
        """
        Extend the URL with path or query parameters.

        Usage:
            url.extend("path")             # Append path component
            url.extend("param", value)     # Add single query parameter
            url.extend({"p1": v1, ...})    # Add multiple query parameters

        Returns:
            A new Url instance with the changes applied
        """
        # Case 1: Dictionary of parameters
        if len(args) == 1 and isinstance(args[0], dict):
            params = args[0]
            return self._extend_with_params(params)

        # Case 2: Key-value parameter pair
        elif len(args) == 2:
            param_name, param_value = args
            return self._extend_with_params({param_name: param_value})

        # Case 3: Path component
        elif len(args) == 1:
            path_component = args[0]
            return self._extend_with_path(path_component)

        # Invalid usage
        else:
            raise ValueError("Invalid arguments for extend()")

    def _extend_with_params(self, params: Dict[str, Any]) -> "Url":
        """Add query parameters to URL."""
        current_params = self.query_params
        current_params.update(params)

        query_string = urllib.parse.urlencode(current_params)

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
        if path.startswith("/"):
            # Replace path
            return Url(f"{self.scheme}://{self.netloc}{path}")
        else:
            # Join with existing path
            current = self.path
            if current and not current.endswith("/"):
                current += "/"
            return Url(f"{self.scheme}://{self.netloc}{current}{path}")

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
