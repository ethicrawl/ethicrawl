from .http_client import HttpClient
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
from typing import List, Dict, Any, Optional, TypedDict, Pattern, Union
import time
import re


class SitemapUrlInfo(TypedDict, total=False):
    url: str
    lastmod: Optional[str]
    changefreq: Optional[str]
    priority: Optional[float]


class SitemapResult:
    def __init__(self, sitemap_handler, sitemap_urls):
        self._handler = sitemap_handler
        self._sitemap_urls = sitemap_urls

    def __iter__(self):
        """Make the result iterable like a list"""
        return iter(self._sitemap_urls)

    def __len__(self):
        """Return the length when using len()"""
        return len(self._sitemap_urls)

    def __getitem__(self, index):
        """Allow array-style access"""
        return self._sitemap_urls[index]

    def __str__(self):
        """String representation"""
        return str(self._sitemap_urls)

    def __repr__(self):
        """Formal representation"""
        return repr(self._sitemap_urls)

    def links(
        self, filter_pattern: Optional[Union[str, Pattern]] = None
    ) -> List[SitemapUrlInfo]:
        """
        Extract all URL entries from the sitemaps, optionally filtered by a pattern.

        This method parses all sitemap XML files and extracts structured URL data including:
        - url: The full URL location
        - lastmod: Last modification date (if available)
        - changefreq: Change frequency like 'daily', 'weekly' (if available)
        - priority: Priority value from 0.0 to 1.0 (if available)

        Args:
            filter_pattern (str or re.Pattern, optional):
                A string to match using simple 'in' comparison,
                or a compiled regex pattern to match using re.search

        Returns:
            List[SitemapUrlInfo]: List of URL information dictionaries,
                                 or empty list if no URLs match or are found

        Example:
            String pattern:
            >>> sitemap_result.links("/p/")

            Regex pattern:
            >>> import re
            >>> pattern = re.compile(r'/p/[A-Z0-9]+')
            >>> sitemap_result.links(pattern)

            Results:
            [
                {
                    "url": "https://example.com/p/product-123",
                    "lastmod": "2025-03-01",
                    "changefreq": "weekly",
                    "priority": 0.8
                },
                ...
            ]
        """
        # Parse all sitemaps to get URL elements
        urls = self._handler.parse_url_elements(self._sitemap_urls)

        # Return all if no filter
        if not filter_pattern:
            return urls

        # Handle regex pattern
        if hasattr(filter_pattern, "search"):  # Check if it's a regex pattern
            filtered_urls = [
                url
                for url in urls
                if "url" in url and filter_pattern.search(url["url"])
            ]
            return filtered_urls

        # Handle string pattern (simple 'in' matching)
        filtered_urls = [
            url for url in urls if "url" in url and filter_pattern in url["url"]
        ]
        return filtered_urls


class SitemapsHandler:
    """Handler for sitemap discovery and processing."""

    # Common sitemap file locations
    DEFAULT_SITEMAP_PATHS = [
        "/sitemap.xml",
        "/sitemap_index.xml",
        "/sitemaps/sitemap.xml",
        "/sitemap/sitemap.xml",
        "/sitemap-index.xml",
    ]

    # Maximum recursion depth for sitemap indexes
    MAX_SITEMAP_RECURSION = 5
    # Maximum number of sitemaps to process
    MAX_SITEMAPS = 100

    def __init__(
        self, http_client: HttpClient, base_url: str, sitemaps: list = None
    ) -> None:
        """
        Initialize the sitemaps handler.

        Args:
            http_client (HttpClient): HTTP client for fetching sitemaps
            base_url (str): Base URL for the site
            sitemaps (list, optional): Initial list of sitemap URLs
        """
        self._http_client = http_client
        self._base_url = base_url
        self._sitemaps = sitemaps or []
        self._response_cache = {}  # Cache for HTTP responses

        # If no sitemaps provided but we have a base URL, check default locations
        if not self._sitemaps and self._base_url:
            self._check_default_sitemap_locations()

    @property
    def sitemaps(self) -> list:
        """Get the list of sitemap URLs."""
        return self._sitemaps

    def _get_with_cache(self, url):
        """
        Get URL content with caching.

        Args:
            url (str): URL to fetch

        Returns:
            HttpResponse: The response object
        """
        # Check cache first
        if url in self._response_cache:
            return self._response_cache[url]

        # Not in cache, fetch and store
        response = self._http_client.get(url)
        if response and response.status_code == 200:
            self._response_cache[url] = response

        return response

    def discover(
        self,
        pattern: Optional[Union[str, Pattern]] = None,
        include_index_contents: bool = True,
    ):
        """
        Discover sitemap URLs, optionally filtered by a pattern.

        Args:
            pattern (str or re.Pattern, optional):
                If provided, only return sitemaps matching this pattern:
                - String pattern uses 'in' operator for substring matching
                - Regex pattern uses pattern.search() for matching
            include_index_contents (bool): Whether to parse sitemap indexes and include their contents

        Returns:
            SitemapResult: Object containing discovered sitemap URLs
        """
        # Get the base list (all sitemaps)
        sitemaps = self._sitemaps.copy()

        # Apply filter if provided
        if pattern:
            if hasattr(pattern, "search"):  # Check if it's a regex pattern
                sitemaps = [url for url in sitemaps if pattern.search(url)]
            else:  # Treat as string
                sitemaps = [url for url in sitemaps if pattern in url]

        # Track processed sitemaps to avoid loops
        processed_sitemaps = set()
        # Results list
        valid_sitemaps = []
        # Sitemaps to check
        sitemaps_to_check = sitemaps.copy()

        # Process each sitemap
        while sitemaps_to_check and len(processed_sitemaps) < self.MAX_SITEMAPS:
            sitemap_url = sitemaps_to_check.pop(0)

            # Skip already processed
            if sitemap_url in processed_sitemaps:
                continue

            processed_sitemaps.add(sitemap_url)

            try:
                # Try to fetch the sitemap with cache
                response = self._get_with_cache(sitemap_url)
                if response and response.status_code == 200:
                    valid_sitemaps.append(sitemap_url)

                    # If this is a sitemap index and we want to include contents
                    if include_index_contents and self._is_sitemap_index(response.text):
                        # Extract child sitemaps
                        child_sitemaps = self._extract_child_sitemaps(response.text)

                        # Add any new ones to our processing list
                        for child_url in child_sitemaps:
                            if (
                                child_url not in processed_sitemaps
                                and child_url not in sitemaps_to_check
                                and len(sitemaps_to_check) + len(processed_sitemaps)
                                < self.MAX_SITEMAPS
                            ):
                                sitemaps_to_check.append(child_url)

                                # Also add to main sitemap list if not there
                                if child_url not in self._sitemaps:
                                    self._sitemaps.append(child_url)
                elif response and response.status_code == 404:
                    # Remove from the sitemap list if it's a 404
                    self.remove_sitemap(sitemap_url)
            except Exception:
                # Remove on error
                self.remove_sitemap(sitemap_url)

        return SitemapResult(self, valid_sitemaps)

    def parse_url_elements(self, sitemap_urls):
        """
        Parse a list of sitemap URLs and extract URL elements.

        Args:
            sitemap_urls (list): List of sitemap URLs to parse

        Returns:
            list: List of dictionaries with URL information
        """
        all_urls = []

        # Process each sitemap
        for sitemap_url in sitemap_urls:
            try:
                # Get the sitemap content from cache or fetch it
                response = self._get_with_cache(sitemap_url)
                if not response or response.status_code != 200:
                    continue

                # Parse the XML
                try:
                    root = ET.fromstring(response.text)
                except Exception:
                    continue

                # Define XML namespaces - FIXED to handle default namespace
                # This is the key change - using empty string as key for default namespace
                namespaces = {
                    "": "http://www.sitemaps.org/schemas/sitemap/0.9",
                    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
                }

                # Find URL elements - try both approaches
                url_elements = root.findall(".//url", namespaces) or root.findall(
                    ".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"
                )

                # Process each URL element
                for url_elem in url_elements:
                    url_info = {}

                    # Required <loc> element - try multiple ways to handle namespace
                    loc_methods = [
                        lambda: url_elem.find("loc", namespaces),
                        lambda: url_elem.find(
                            "{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
                        ),
                        lambda: url_elem.find(
                            "sm:loc",
                            {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"},
                        ),
                        lambda: url_elem.find("loc"),
                    ]

                    loc_elem = None
                    for method in loc_methods:
                        try:
                            loc_elem = method()
                            if loc_elem is not None and loc_elem.text:
                                break
                        except Exception:
                            continue

                    if loc_elem is not None and loc_elem.text:
                        loc = loc_elem.text.strip()
                        url_info["url"] = loc
                    else:
                        # Skip URL entries without loc
                        continue

                    # Apply same approach for metadata elements
                    # Optional <lastmod> element
                    lastmod_methods = [
                        lambda: url_elem.find("lastmod", namespaces),
                        lambda: url_elem.find(
                            "{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod"
                        ),
                        lambda: url_elem.find(
                            "sm:lastmod",
                            {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"},
                        ),
                        lambda: url_elem.find("lastmod"),
                    ]

                    for method in lastmod_methods:
                        try:
                            lastmod_elem = method()
                            if lastmod_elem is not None and lastmod_elem.text:
                                url_info["lastmod"] = lastmod_elem.text.strip()
                                break
                        except Exception:
                            continue

                    # Optional <changefreq> element
                    changefreq_methods = [
                        lambda: url_elem.find("changefreq", namespaces),
                        lambda: url_elem.find(
                            "{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq"
                        ),
                        lambda: url_elem.find(
                            "sm:changefreq",
                            {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"},
                        ),
                        lambda: url_elem.find("changefreq"),
                    ]

                    for method in changefreq_methods:
                        try:
                            changefreq_elem = method()
                            if changefreq_elem is not None and changefreq_elem.text:
                                url_info["changefreq"] = changefreq_elem.text.strip()
                                break
                        except Exception:
                            continue

                    # Optional <priority> element
                    priority_methods = [
                        lambda: url_elem.find("priority", namespaces),
                        lambda: url_elem.find(
                            "{http://www.sitemaps.org/schemas/sitemap/0.9}priority"
                        ),
                        lambda: url_elem.find(
                            "sm:priority",
                            {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"},
                        ),
                        lambda: url_elem.find("priority"),
                    ]

                    for method in priority_methods:
                        try:
                            priority_elem = method()
                            if priority_elem is not None and priority_elem.text:
                                try:
                                    url_info["priority"] = float(
                                        priority_elem.text.strip()
                                    )
                                    break
                                except ValueError:
                                    pass
                        except Exception:
                            continue

                    # Add this URL to our results
                    all_urls.append(url_info)

            except Exception as e:
                # Log the error but continue with next sitemap
                print(f"Error parsing {sitemap_url}: {e}")

        return all_urls

    def _is_sitemap_index(self, content):
        """Check if XML content is a sitemap index."""
        try:
            root = ET.fromstring(content)
            # Check tag name (account for namespaces)
            root_tag = root.tag
            if root_tag.endswith("sitemapindex"):
                return True

            # Check for sitemap elements with namespaces
            namespaces = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            sitemap_elements = root.findall(".//sm:sitemap/sm:loc", namespaces)
            return len(sitemap_elements) > 0

        except Exception:
            return False

    def _extract_child_sitemaps(self, content):
        """Extract child sitemap URLs from a sitemap index."""
        try:
            root = ET.fromstring(content)
            namespaces = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

            # Try with namespace first
            sitemap_elements = root.findall(".//sm:sitemap/sm:loc", namespaces)

            # If none found, try without namespace
            if not sitemap_elements:
                sitemap_elements = root.findall(".//sitemap/loc")

            # Extract URLs
            urls = []
            for element in sitemap_elements:
                if element.text and element.text.strip():
                    urls.append(element.text.strip())
            return urls

        except Exception:
            return []

    def remove_sitemap(self, sitemap_url):
        """
        Remove a sitemap URL from the list.

        Args:
            sitemap_url (str): Sitemap URL to remove
        """
        if sitemap_url in self._sitemaps:
            self._sitemaps.remove(sitemap_url)
            # Also remove from cache if present
            if sitemap_url in self._response_cache:
                del self._response_cache[sitemap_url]

    def _check_default_sitemap_locations(self) -> None:
        """
        Check common default sitemap locations if none were specified in robots.txt.
        This helps discover sitemaps for sites that don't list them in robots.txt.
        """
        for path in self.DEFAULT_SITEMAP_PATHS:
            sitemap_url = f"{self._base_url.rstrip('/')}{path}"
            try:
                # Use caching here too
                response = self._get_with_cache(sitemap_url)
                if response and response.status_code == 200:
                    # If we get a valid response, this is likely a sitemap
                    self._sitemaps.append(sitemap_url)
            except Exception:
                pass  # Silently continue if we can't access a potential sitemap
