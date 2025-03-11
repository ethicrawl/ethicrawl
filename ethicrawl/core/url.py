import urllib.parse
import socket
from typing import Optional, Dict, Any, Union

from functools import wraps


def http_only(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._parsed.scheme not in ["http", "https"]:
            raise ValueError("Only valid for HTTP and HTTPS urls")
        return func(self, *args, **kwargs)

    return wrapper


class Url:

    def __init__(self, url: Union[str, "Url"], validate: bool = False):
        if isinstance(url, Url):
            url = str(url)

        self._parsed = urllib.parse.urlparse(url)

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
                socket.gethostbyname(self._parsed.netloc)
            except socket.gaierror:
                raise ValueError(f"Cannot resolve hostname: {self._parsed.netloc}")

    @property
    def base(self) -> str:
        """Get scheme and netloc."""
        if self.scheme == "file":
            return "file://"
        return f"{self.scheme}://{self.netloc}"

    @property
    def scheme(self) -> str:
        """Get the URL scheme (http or https)."""
        return self._parsed.scheme

    @http_only
    @property
    def netloc(self) -> str:
        """Get the network location (domain)."""
        return self._parsed.netloc

    @http_only
    @property
    def hostname(self) -> str:
        """Get just the hostname part."""
        return self._parsed.hostname

    @property
    def path(self) -> str:
        """Get the path component."""
        return self._parsed.path

    @http_only
    @property
    def params(self) -> str:
        """Get URL parameters."""
        return self._parsed.params

    @http_only
    @property
    def query(self) -> str:
        """Get the query string."""
        return self._parsed.query

    @http_only
    @property
    def query_params(self) -> Dict[str, Any]:
        """Get parsed query parameters as a dictionary."""
        return dict(urllib.parse.parse_qsl(self._parsed.query))

    @http_only
    @property
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
        if self.scheme == "file":
            if path.startswith("/"):
                # Replace path for file URLs
                return Url(f"file://{path}")
            else:
                # Join with existing path
                current = self.path
                if current and not current.endswith("/"):
                    current += "/"
                return Url(f"file://{current}{path}")
        else:
            # HTTP(S) path extension
            if path.startswith("/"):
                return Url(f"{self.scheme}://{self.netloc}{path}")
            else:
                current = self.path
                if current and not current.endswith("/"):
                    current += "/"
                return Url(f"{self.scheme}://{self.netloc}{current}{path}")

    def extend(self, *args, **kwargs) -> "Url":
        """
        Extend the URL with path or query parameters.

        For HTTP(S) URLs, supports path and query parameter extension.
        For file URLs, only supports path extension.
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
