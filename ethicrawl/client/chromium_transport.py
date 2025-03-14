from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .transport import Transport

from ethicrawl.core.context import Context

from .http_response import HttpResponse
from .http_request import HttpRequest
import time
import json

# import html
import lxml
from lxml import html, etree


class ChromiumTransport(Transport):
    """Transport implementation using Chromium for JavaScript-rendered content."""

    def __init__(self, context: Context, headless=True, wait_time=3):
        """
        Initialize Chromium transport.

        Args:
            context (Context): The application context
            headless (bool): Run browser in headless mode
            wait_time (int): Time to wait for JavaScript to execute in seconds
        """
        self._context = context
        self._logger = self._context.logger("client.chromium")
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
        from ethicrawl.config import Config

        if hasattr(Config().http, "proxies") and Config().http.proxies:
            proxies = Config().http.proxies

            # If both HTTP and HTTPS use the same proxy (common case)
            if proxies.get("http") == proxies.get("https") and proxies.get("http"):
                options.add_argument(f'--proxy-server={proxies["http"]}')
            else:
                # Handle case when HTTP and HTTPS proxies are different
                if proxies.get("http"):
                    options.add_argument(f'--proxy-server=http={proxies["http"]}')
                if proxies.get("https"):
                    options.add_argument(f'--proxy-server=https={proxies["https"]}')

        # Enable performance logging - critical for getting network details
        options.set_capability(
            "goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"}
        )

        # Initialize the driver
        self.driver = webdriver.Chrome(options=options)

    @property
    def user_agent(self):
        """
        Get the User-Agent string used by Chromium.

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
    def user_agent(self, agent):
        """
        Set the User-Agent string for Chromium.
        This is a passive operation - it only records what was passed,
        but doesn't actually modify the browser's User-Agent.

        Args:
            agent (str): The User-Agent string that was requested
        """
        # For Chromium, we just record that this was requested but don't modify
        # the browser's actual User-Agent to maintain authenticity
        print(
            f"Note: User-Agent override requested to '{agent}' but Chromium uses browser's native User-Agent"
        )

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Make a GET request using Chromium with full network information capture.

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
                print(
                    f"Note: Headers requested ({header_names}) but Chromium has limited header support"
                )

            # Update user agent information
            self._user_agent = self.driver.execute_script("return navigator.userAgent;")

            # Wait for page to load
            try:
                WebDriverWait(self.driver, timeout or 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception as e:
                self._logger.debug(f"Page load wait timed out (continuing anyway): {e}")

            # Additional wait for dynamic content if specified
            if self._wait_time:
                time.sleep(self._wait_time)

            # Get page source and final URL
            page_source = self.driver.page_source
            final_url = self.driver.current_url

            # Extract network information from performance logs
            status_code, response_headers, mime_type = self._extract_network_info(
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
                request=request,
                status_code=status_code or 200,
                text=content_bytes.decode("utf-8", errors="replace"),
                headers=headers,
                content=content_bytes,
            )

            return response

        except Exception as e:
            raise IOError(f"Error fetching {url} with Chromium: {e}")

    def _extract_xml_content(self, content_str: str) -> bytes:
        """
        Extract XML content when Chrome/Chromium renders XML as HTML.

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
                if xml_div and len(xml_div) > 0:
                    # Get the XML content as string
                    xml_content = "".join(
                        etree.tostring(child, encoding="unicode")
                        for child in xml_div[0].getchildren()
                    )
                    return xml_content.encode("utf-8")
        except Exception as e:
            print(f"Warning: Failed to extract XML from browser response: {e}")

        # Return original content encoded as bytes if extraction failed
        return content_str.encode("utf-8")

    def _extract_network_info(self, requested_url, final_url):
        """
        Extract network information from performance logs.

        Returns:
            tuple: (status_code, response_headers, mime_type)
        """
        try:
            logs = self.driver.get_log("performance")
            status_code = None
            headers = {}
            mime_type = None

            # First try to find exact URL match
            for entry in logs:
                try:
                    log_data = json.loads(entry["message"])["message"]
                    if log_data["method"] != "Network.responseReceived":
                        continue

                    response = log_data.get("params", {}).get("response", {})
                    url = response.get("url", "")

                    # Check for both the requested URL and final URL (after redirects)
                    if url == requested_url or url == final_url:
                        status_code = response.get("status")
                        mime_type = response.get("mimeType")

                        # Get headers if available
                        for key, value in response.get("headers", {}).items():
                            headers[key] = value

                        # If we found an exact match, return immediately
                        return status_code, headers, mime_type
                except Exception as e:
                    self._logger.debug(f"Error processing network log entry: {e}")
                    continue

            # If no exact match, look for main document response
            for entry in logs:
                try:
                    log_data = json.loads(entry["message"])["message"]
                    if log_data["method"] != "Network.responseReceived":
                        continue

                    params = log_data.get("params", {})
                    resource_type = params.get("type")

                    # Find the main document response
                    if resource_type == "Document":
                        response = params.get("response", {})
                        status_code = response.get("status")
                        mime_type = response.get("mimeType")

                        # Get headers
                        for key, value in response.get("headers", {}).items():
                            headers[key] = value

                        return status_code, headers, mime_type
                except Exception as e:
                    self._logger.debug(f"Error processing document response log: {e}")
                    continue

            # Default fallback
            return status_code, headers, mime_type

        except Exception as e:
            print(f"Error extracting network info: {e}")
            return None, {}, None

    def __del__(self):
        """Close browser when transport is garbage collected."""
        try:
            if hasattr(self, "driver") and self.driver:
                self.driver.quit()
        except Exception as e:
            # Use the logger if it exists, otherwise we can't log during cleanup
            if hasattr(self, "_logger"):
                self._logger.debug(f"Error closing browser during cleanup: {e}")
