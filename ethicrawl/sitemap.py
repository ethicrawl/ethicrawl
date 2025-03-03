from abc import ABC, abstractmethod
from lxml import etree, html
from lxml.etree import QName
from enum import Enum
import re

from dataclasses import dataclass
from typing import List, Optional, Union
import re
from urllib.parse import urlparse

from .http_client import HttpClient


class SitemapHelper:
    """Helper class with utility methods for sitemap processing."""

    @staticmethod
    def validate_url(url: str) -> str:
        """
        Validate and normalize URL.

        Args:
            url: URL string

        Returns:
            str: Normalized URL

        Raises:
            ValueError: If URL is invalid
        """
        if url is None or len(url) == 0:
            raise ValueError("URL cannot be empty")

        # Basic URL validation
        try:
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                raise ValueError(f"URL must include scheme and domain: {url}")
        except Exception as e:
            raise ValueError(f"Invalid URL format: {str(e)}")

        return url.strip()


@dataclass
class SitemapIndexUrl:
    """Represents a URL from a sitemap index"""

    loc: str  # REQUIRED: The location URI of a document. The URI must conform to RFC 2396 (http://www.ietf.org/rfc/rfc2396.txt)
    lastmod: Optional[str] = (
        None  # OPTIONAL: The date the document was last modified. The date must conform to the W3C DATETIME format (http://www.w3.org/TR/NOTE-datetime). Example: 2005-05-10 Lastmod may also contain a timestamp. Example: 2005-05-10T17:33:30+08:00
    )

    @staticmethod
    def _validate_url(url: str) -> str:
        """
        Validate and normalize URL.

        Args:
            url: URL string

        Returns:
            str: Normalized URL

        Raises:
            ValueError: If URL is invalid
        """

        if url is None or len(url) == 0:
            raise ValueError("URL cannot be empty")

        # Basic URL validation
        try:
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                raise ValueError(f"URL must include scheme and domain: {url}")
        except Exception as e:
            raise ValueError(f"Invalid URL format: {str(e)}")

        return url.strip()

    @staticmethod
    def _validate_lastmod(value: Optional[str]) -> Optional[str]:
        """
        Validate lastmod date format.

        Args:
            value: Date string in W3C format

        Returns:
            str: Validated date string

        Raises:
            ValueError: If date format is invalid
        """
        if not value:
            return None

        # Strip whitespace
        value = value.strip()

        # Basic format validation for common patterns
        # Complete W3C datetime validation would be more complex
        date_patterns = [
            r"^\d{4}-\d{2}-\d{2}$",  # YYYY-MM-DD
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([+-]\d{2}:\d{2}|Z)$",  # YYYY-MM-DDThh:mm:ssTZD
        ]

        if not any(re.match(pattern, value) for pattern in date_patterns):
            raise ValueError(f"Invalid lastmod date format: {value}")

        return value

    def __post_init__(self):
        """
        Validate and normalize all fields after initialization.
        """
        # Validate and normalize URL
        self.loc = SitemapHelper.validate_url(self.loc)

        # Validate lastmod
        self.lastmod = self._validate_lastmod(self.lastmod)


@dataclass
class SitemapUrlsetUrl(SitemapIndexUrl):
    """Represents a URL from a sitemap urlset."""

    changefreq: Optional[str] = (
        None  # OPTIONAL: Indicates how frequently the content at a particular URL is likely to change. The value "always" should be used to describe documents that change each time they are accessed. The value "never" should be used to describe archived URLs. Please note that web crawlers may not necessarily crawl pages marked "always" more often. Consider this element as a friendly suggestion and not a command.
    )
    priority: Optional[float] = (
        None  #  OPTIONAL: The priority of a particular URL relative to other pages on the same site. The value for this element is a number between 0.0 and 1.0 where 0.0 identifies the lowest priority page(s). The default priority of a page is 0.5. Priority is used to select between pages on your site. Setting a priority of 1.0 for all URLs will not help you, as the relative priority of pages on your site is what will be considered.
    )

    _valid_change_freqs = [
        "always",
        "hourly",
        "daily",
        "weekly",
        "monthly",
        "yearly",
        "never",
    ]

    @staticmethod
    def _validate_priority(value: Union[str, float, None]) -> Optional[float]:
        """
        Validate and convert priority value.

        Args:
            value: Priority value as string or float

        Returns:
            float: Normalized priority value

        Raises:
            ValueError: If priority is not between 0.0 and 1.0
        """
        if value is None:
            return None

        # Convert string to float if needed
        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                raise ValueError(f"Priority must be a number, got '{value}'")

        # Validate range
        if not (0.0 <= value <= 1.0):
            raise ValueError(f"Priority must be between 0.0 and 1.0, got {value}")

        return value

    def __post_init__(self):
        """
        Validate and normalize all fields after initialization.
        """
        # Validate and normalize URL
        self.loc = self._validate_url(self.loc)

        # Validate lastmod
        self.lastmod = self._validate_lastmod(self.lastmod)

        # Validate changefreq
        if self.changefreq is not None:
            self.changefreq = self.changefreq.strip().lower()
            if self.changefreq not in self._valid_change_freqs:
                raise ValueError(f"Invalid change frequency: {self.changefreq}")

        # Validate priority
        self.priority = self._validate_priority(self.priority)


class SitemapType(Enum):
    """Enum for the two possible sitemap types."""

    INDEX = "sitemapindex"
    URLSET = "urlset"
    UNDEFINED = "undefined"


class SitemapError(Exception):
    """Exception raised for sitemap parsing errors."""

    pass


class SitemapTree:
    pass


class SitemapNode(ABC):
    """Should never be instantiated directly"""

    SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

    @staticmethod
    def _escape_unescaped_ampersands(xml_document: str) -> str:
        """Escape unescaped ampersands in XML content."""
        pattern = r"&(?!(?:[a-zA-Z]+|#[0-9]+|#x[0-9a-fA-F]+);)"
        return re.sub(pattern, "&amp;", xml_document)

    @staticmethod
    def _preparse(xml_string: str) -> str:
        """Preprocess XML to fix common issues before parsing."""
        xml_string = SitemapNode._escape_unescaped_ampersands(xml_string)
        return xml_string

    def __init__(self, document: str) -> None:
        try:
            document = self._preparse(document)
            self._root = etree.fromstring(document.encode("utf-8"))
        except Exception as e:
            raise SitemapError(f"Invalid XML syntax: {str(e)}")

        if self._root.nsmap[None] != self.SITEMAP_NS:
            raise SitemapError(
                f"Required default namespace not found: {self.SITEMAP_NS}"
            )
        try:
            local_name = QName(self._root.tag).localname
        except:
            raise SitemapError(f"Root tag does not have a name")

        if local_name == "urlset":
            self._type = SitemapType.URLSET
        elif local_name == "sitemapindex":
            self._type = SitemapType.INDEX
        else:
            self._type = SitemapType.UNDEFINED

    @property
    def type(self) -> SitemapType:
        """Get the type of this sitemap node."""
        return self._type

    @property
    @abstractmethod
    def items(self) -> List:
        """
        Get the items in this sitemap.

        Returns:
            List: Either List[SitemapUrlsetUrl] (for urlset) or List[SitemapIndexUrl] (for index)
        """
        pass


class SitemapIndexNode(SitemapNode):
    """Node representing a sitemap index."""

    def __init__(self, document: str) -> None:
        super().__init__(document)
        self._sitemaps = None
        local_name = QName(self._root.tag).localname

        if self._type != SitemapType.INDEX:
            raise SitemapError(
                f"Not a sitemap index document. Root element is '{local_name}', expected 'sitemapindex'"
            )

    @property
    def items(self) -> List[SitemapIndexUrl]:
        if self._sitemaps is None:
            self._sitemaps = self._parse_sitemaps()
        return self._sitemaps

    def _parse_sitemaps(self) -> List[SitemapIndexUrl]:
        """Parse sitemap references from a sitemap index."""
        sitemaps = []
        nsmap = {None: self.SITEMAP_NS}

        # Find all sitemap elements
        for sitemap_elem in self._root.findall(".//sitemap", namespaces=nsmap):
            try:
                # Get the required loc element
                loc_elem = sitemap_elem.find("loc", namespaces=nsmap)
                if loc_elem is None or not loc_elem.text:
                    continue

                # Get optional lastmod element
                lastmod_elem = sitemap_elem.find("lastmod", namespaces=nsmap)

                # Create SitemapIndexUrl object (only loc and lastmod)
                sitemap_url = SitemapIndexUrl(
                    loc=loc_elem.text,
                    lastmod=lastmod_elem.text if lastmod_elem is not None else None,
                )

                sitemaps.append(sitemap_url)
            except ValueError as e:
                print(f"Error parsing sitemap reference: {e}")

        return sitemaps


class UrlsetNode(SitemapNode):
    """Node representing a sitemap urlset."""

    def __init__(self, document: str) -> None:
        super().__init__(document)
        self._urls = None
        local_name = QName(self._root.tag).localname

        if self._type != SitemapType.URLSET:
            raise SitemapError(
                f"Not a urlset document. Root element is '{local_name}', expected 'urlset'"
            )

    @property
    def items(self) -> List[SitemapUrlsetUrl]:
        if self._urls is None:
            pass
            self._urls = self._parse_urls()
        return self._urls

    def _parse_urls(self) -> List[SitemapUrlsetUrl]:
        """Parse URLs from a sitemap urlset."""
        urls = []
        nsmap = {None: self.SITEMAP_NS}  # namespace mapping for the default namespace

        # Find all url elements
        for url_elem in self._root.findall(".//url", namespaces=nsmap):
            try:
                # Get the required loc element
                loc_elem = url_elem.find("loc", namespaces=nsmap)
                if loc_elem is None or not loc_elem.text:
                    continue

                # Get optional elements
                lastmod_elem = url_elem.find("lastmod", namespaces=nsmap)
                changefreq_elem = url_elem.find("changefreq", namespaces=nsmap)
                priority_elem = url_elem.find("priority", namespaces=nsmap)

                # Create SitemapUrlsetUrl object - validation happens in __post_init__
                url = SitemapUrlsetUrl(
                    loc=loc_elem.text,
                    lastmod=lastmod_elem.text if lastmod_elem is not None else None,
                    changefreq=(
                        changefreq_elem.text if changefreq_elem is not None else None
                    ),
                    priority=priority_elem.text if priority_elem is not None else None,
                )

                urls.append(url)
            except ValueError as e:
                print(f"Error parsing URL: {e}")

        return urls


class SitemapFactory:
    """Factory for creating sitemap nodes of the appropriate type."""

    @staticmethod
    def _extract_xml_from_browser_response(content: bytes) -> str:
        """
        Extract XML content from a browser-rendered XML page.

        Args:
            content: Raw response content from browser

        Returns:
            str: Raw XML content or original content if no wrapper detected
        """
        content_str = content.decode("utf-8", errors="replace")

        # Check if this is a browser-rendered XML page
        if '<div id="webkit-xml-viewer-source-xml">' in content_str:
            try:
                # Parse HTML
                root = html.fromstring(content_str)

                # Extract content from the XML viewer div
                xml_div = root.xpath('//div[@id="webkit-xml-viewer-source-xml"]')
                if xml_div and len(xml_div) > 0:
                    # Get the XML content as string
                    xml_content = "".join(
                        etree.tostring(child, encoding="unicode")
                        for child in xml_div[0].getchildren()
                    )
                    return xml_content
            except Exception as e:
                print(f"Warning: Failed to extract XML from browser response: {e}")

        # Return original content if extraction failed
        return content_str

    @staticmethod
    def old_create(document: str) -> Union[UrlsetNode, SitemapIndexNode]:
        """
        Create the appropriate sitemap node based on the document type.

        Args:
            document: XML sitemap document

        Returns:
            Either UrlsetNode or SitemapIndexNode

        Raises:
            SitemapError: If the document is invalid or has an unsupported type
        """
        # First determine the type of document
        try:
            # Pre-process and parse document
            document = SitemapNode._preparse(document)
            root = etree.fromstring(document.encode("utf-8"))

            # Check namespace
            if root.nsmap[None] != SitemapNode.SITEMAP_NS:
                raise SitemapError(
                    f"Required default namespace not found: {SitemapNode.SITEMAP_NS}"
                )

            # Get root element name
            local_name = QName(root.tag).localname

            # Create appropriate node type
            if local_name == "urlset":
                return UrlsetNode(document)
            elif local_name == "sitemapindex":
                return SitemapIndexNode(document)
            else:
                raise SitemapError(f"Unsupported sitemap type: {local_name}")

        except Exception as e:
            if isinstance(e, SitemapError):
                raise
            raise SitemapError(f"Error creating sitemap node: {str(e)}")

    @staticmethod
    def create(sitemap_url: SitemapIndexUrl, http_client: HttpClient) -> SitemapNode:
        """
        Create a sitemap node by fetching and parsing a remote URL.

        Args:
            sitemap_url: The SitemapIndexUrl to fetch
            http_client: HttpClient instance for making requests

        Returns:
            A sitemap node of the appropriate type

        Raises:
            SitemapError: For any errors during fetch or parse
        """
        try:
            # URL is already validated in the SitemapIndexUrl object
            url = sitemap_url.loc

            # Fetch the sitemap
            response = http_client.get(url)

            # Check for success
            if not response or response.status_code != 200:
                raise SitemapError(
                    f"Failed to fetch sitemap from {url}: {response.status_code if response else 'No response'}"
                )

            document = SitemapFactory._extract_xml_from_browser_response(
                response.content
            )

            return SitemapFactory.create(document)

        except Exception as e:
            if isinstance(e, SitemapError):
                raise
            raise SitemapError(
                f"Error creating sitemap from URL {sitemap_url.loc}: {str(e)}"
            )

    @staticmethod
    def create_from_url(
        sitemap_url: SitemapIndexUrl, http_client: HttpClient
    ) -> SitemapNode:
        """
        Create a sitemap node by fetching and parsing a remote URL.

        Args:
            sitemap_url: The SitemapIndexUrl to fetch
            http_client: HttpClient instance for making requests

        Returns:
            A sitemap node of the appropriate type

        Raises:
            SitemapError: For any errors during fetch or parse
        """
        try:
            # URL is already validated in the SitemapIndexUrl object
            url = sitemap_url.loc

            # Fetch the sitemap
            response = http_client.get(url)

            # Check for success
            if not response or response.status_code != 200:
                raise SitemapError(
                    f"Failed to fetch sitemap from {url}: {response.status_code if response else 'No response'}"
                )

            # Extract XML from browser-rendered response if needed
            document = SitemapFactory._extract_xml_from_browser_response(
                response.content
            )

            # Parse the extracted content
            return SitemapFactory.create(document)

        except Exception as e:
            if isinstance(e, SitemapError):
                raise
            raise SitemapError(
                f"Error creating sitemap from URL {sitemap_url.loc}: {str(e)}"
            )

    @staticmethod
    def create_index_from_urls(
        sitemap_urls: List[str], lastmod: str = "2025-03-01"
    ) -> SitemapIndexNode:
        """
        Create a new SitemapIndexNode from a list of sitemap URLs.

        Args:
            sitemap_urls: List of sitemap URL strings
            lastmod: Optional lastmod date to use for all sitemaps

        Returns:
            SitemapIndexNode: A sitemap index containing the provided URLs

        Raises:
            SitemapError: If the sitemap generation fails
        """
        try:
            # Generate the sitemap XML directly as a string
            xml_lines = [
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">',
            ]

            # Add each sitemap URL as an entry
            for url in sitemap_urls:
                try:
                    # Validate and normalize the URL
                    url = SitemapHelper.validate_url(url)
                    xml_lines.append("  <sitemap>")
                    xml_lines.append(f"    <loc>{url}</loc>")
                    if lastmod:
                        xml_lines.append(f"    <lastmod>{lastmod}</lastmod>")
                    xml_lines.append("  </sitemap>")
                except ValueError as e:
                    print(f"Skipping invalid URL: {e}")
                    continue

            # Close the root element
            xml_lines.append("</sitemapindex>")

            # Join into a single string
            xml_string = "\n".join(xml_lines)

            # Use the existing create method to handle parsing and validation
            return SitemapFactory.create(xml_string)

        except Exception as e:
            import traceback

            error_details = traceback.format_exc()
            if isinstance(e, SitemapError):
                raise
            raise SitemapError(
                f"Error creating sitemap index: {str(e)}\n{error_details}"
            )
