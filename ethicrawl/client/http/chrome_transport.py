from json import loads
from time import sleep
from typing import Any

from lxml import etree, html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ethicrawl.client import Transport
from ethicrawl.config import Config
from ethicrawl.context import Context

from .http_request import HttpRequest
from .http_response import HttpResponse


class ChromeTransport(Transport):
    """Transport implementation using Chrome for JavaScript-rendered content."""

    def __init__(self, context: Context, headless=True, wait_time=3):
        """
        Initialize Chrome transport.

        Args:
            context (Context): The application context
            headless (bool): Run browser in headless mode
            wait_time (int): Time to wait for JavaScript to execute in seconds
        """
        self._context = context
        self._logger = self._context.logger("client.chrome")
        self._wait_time = wait_time
        self._user_agent = None  # Will be populated after first request

        # Set up Chrome options
        options = Options()
        if headless:
            options.add_argument("--headless")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        # Set up proxy if configured
        http_proxy = Config().http.proxies.http
        https_proxy = Config().http.proxies.https

        if http_proxy or https_proxy:
            # If both HTTP and HTTPS use the same proxy (common case)
            if http_proxy and https_proxy and str(http_proxy) == str(https_proxy):
                options.add_argument(f"--proxy-server={http_proxy}")
            else:
                # Handle case when HTTP and HTTPS proxies are different
                if http_proxy:
                    options.add_argument(f"--proxy-server=http={http_proxy}")
                if https_proxy:
                    options.add_argument(f"--proxy-server=https={https_proxy}")

        # Enable performance logging - critical for getting network details
        options.set_capability(
            "goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"}
        )

        # Initialize the driver
        self.driver = webdriver.Chrome(options=options)

    @property
    def user_agent(self) -> str:
        """
        Get the User-Agent string used by Chrome.

        Returns:
            str: The User-Agent string
        """
        # If we already know the UA, return it
        if self._user_agent:
            return self._user_agent

        # If we haven't made a request yet, get it from the browser
        try:
            # Navigate to a simple page to avoid external requests
            self.driver.get("about:blank")
            # Execute JavaScript to get the user agent
            self._user_agent = self.driver.execute_script("return navigator.userAgent;")
            return self._user_agent
        except Exception as e:
            # Return a default value if we can't determine it yet
            return "Mozilla/5.0 (Unknown) Chrome/Unknown Safari/Unknown"

    @user_agent.setter
    def user_agent(self, agent: str):
        """
        Set the User-Agent string for Chrome.
        This is a passive operation - it only records what was passed,
        but doesn't actually modify the browser's User-Agent.

        Args:
            agent (str): The User-Agent string that was requested
        """
        # For Chrome, we just record that this was requested but don't modify
        # the browser's actual User-Agent to maintain authenticity
        self._logger.debug(
            f"Note: User-Agent override requested to '{agent}' but Chrome uses browser's native User-Agent"
        )

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Make a GET request using Chrome with full network information capture.

        Args:
            url (str): The URL to request
            timeout (int, optional): Request timeout in seconds
            headers (dict, optional): Additional headers (limited support)

        Returns:
            HttpResponse: Standardized response object
        """
        try:

            # Extract parameters from request object
            url = str(request.url)
            timeout = request.timeout

            # Clear logs before request
            if self.driver.get_log("performance"):
                pass  # Just accessing to clear buffer

            # Set page load timeout
            self.driver.set_page_load_timeout(timeout)

            # Navigate to URL
            self.driver.get(url)

            # Note: While we can't directly set most headers in Selenium,
            # we can record that headers were requested
            if request.headers:
                # Just log that headers were requested but can't be fully applied
                header_names = ", ".join(request.headers.keys())
                self._logger.debug(
                    f"Note: Headers requested ({header_names}) but Chrome has limited header support"
                )

            # Update user agent information
            self._user_agent = self.driver.execute_script("return navigator.userAgent;")

            # Wait for page to load
            try:
                WebDriverWait(self.driver, timeout or Config().http.timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception as e:  # pragma: no cover
                self._logger.debug(f"Page load wait timed out (continuing anyway): {e}")

            # Additional wait for dynamic content if specified
            if self._wait_time:
                sleep(self._wait_time)

            # Get page source and final URL
            page_source = self.driver.page_source
            final_url = self.driver.current_url

            # Extract network information from performance logs
            status_code, response_headers, mime_type = self._get_response_information(
                url, final_url
            )

            # Convert page source to bytes for content
            content_bytes = page_source.encode("utf-8")

            # Handle XML content if needed
            if mime_type and ("xml" in mime_type or url.lower().endswith(".xml")):
                # Process XML content when rendered as HTML
                content_bytes = self._extract_xml_content(page_source)

            # Create response headers
            headers = {
                "URL": final_url,
                "Content-Type": mime_type or "text/html",
                **response_headers,
            }

            # Create the response with text properly decoded from content
            response = HttpResponse(
                url=final_url or request.url,
                request=request,
                status_code=status_code or 200,
                text=content_bytes.decode("utf-8", errors="replace"),
                headers=headers,
                content=content_bytes,
            )

            return response

        except Exception as e:  # pragma: no cover
            raise IOError(f"Error fetching {url} with Chrome: {e}")

    def _extract_xml_content(self, content_str: str) -> bytes:
        """
        Extract XML content when Chrome renders XML as HTML.

        Args:
            content_str: Page source as string

        Returns:
            bytes: Raw XML content as bytes
        """
        try:
            # Check if this is a browser-rendered XML page
            if '<div id="webkit-xml-viewer-source-xml">' in content_str:
                # Parse HTML
                parser = etree.HTMLParser(huge_tree=False)
                root = html.fromstring(content_str, parser=parser)

                # Extract content from the XML viewer div
                xml_div = root.xpath('//div[@id="webkit-xml-viewer-source-xml"]')

                if isinstance(xml_div, list) and xml_div:
                    first_div = xml_div[0]

                    xml_content = "".join(
                        etree.tostring(child, encoding="unicode")  # type: ignore
                        for child in list(first_div)
                    )
                    return xml_content.encode("utf-8")

        except Exception as e:  # pragma: no cover
            self._logger.warning(f"Failed to extract XML from browser response: {e}")

        # Return original content encoded as bytes if extraction failed
        return content_str.encode("utf-8")

    def _extract_response_info_from_log_entry(
        self, entry: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, Any]] | None:
        """Process a single performance log entry and extract response data."""
        try:
            log_data = loads(entry["message"])["message"]
            if log_data["method"] != "Network.responseReceived":
                return None

            params = log_data.get("params", {})
            response = params.get("response", {})
            return params, response
        except Exception as e:
            self._logger.debug(f"Error processing log entry: {e}")
            return None

    def _extract_response_info_from_response(
        self, response: dict[str, Any]
    ) -> tuple[int | None, dict[str, str], str | None]:
        """Extract status, headers and MIME type from a response."""
        try:
            status_code = response.get("status")
            mime_type = response.get("mimeType")

            # Extract headers
            headers = {}
            for key, value in response.get("headers", {}).items():
                headers[key] = value
            return status_code, headers, mime_type
        except Exception as e:
            self._logger.debug(f"Error processing log entry: {e}")
            return None, {}, None  # Return 3-tuple with default values

    def _get_response_information(
        self, requested_url: str, final_url: str
    ) -> tuple[int | None, dict[str, str], str | None]:
        # Default values if we can't find anything
        default_status = 200  # Most browsers show content even without status
        default_headers: dict[str, str] = {}
        default_mime = "text/html"  # Assume HTML if not specified
        try:
            logs = self.driver.get_log("performance")
            document_response = None
            for entry in logs:
                result = self._extract_response_info_from_log_entry(entry)
                if not result:
                    # Skip non-response entries
                    continue

                params, response = result
                url = response.get("url", "")

                # First priority: exact URL match
                if url == requested_url or url == final_url:
                    return self._extract_response_info_from_response(response)

                # Second priority: document response (save for fallback)
                if params.get("type") == "Document" and not document_response:
                    document_response = response

            # If we found a document response, use it as fallback
            if document_response:
                return self._extract_response_info_from_response(document_response)

            # Default fallback if no matching response found
            return default_status, default_headers, default_mime

        except Exception as e:  # pragma: no cover
            self._logger.debug(f"Error extracting network info: {e}")
            return default_status, default_headers, default_mime

    def __del__(self):
        """Close browser when transport is garbage collected."""
        try:
            if hasattr(self, "driver") and self.driver:
                self.driver.quit()
        except Exception as e:  # pragma: no cover
            # Use the logger if it exists, otherwise we can't log during cleanup
            if hasattr(self, "_logger"):
                self._logger.debug(f"Error closing browser during cleanup: {e}")
            else:
                raise e
