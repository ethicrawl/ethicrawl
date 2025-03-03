from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .transport import Transport
from .http_response import HttpResponse
import time
import json


class SeleniumTransport(Transport):
    """Transport implementation using Selenium for JavaScript-rendered content."""

    def __init__(self, headless=True, wait_time=3):
        """
        Initialize Selenium transport.

        Args:
            headless (bool): Run browser in headless mode
            wait_time (int): Time to wait for JavaScript to execute in seconds
        """
        self.wait_time = wait_time
        self._user_agent = None  # Will be populated after first request

        # Set up Chrome options
        options = Options()
        if headless:
            options.add_argument("--headless")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        # Enable performance logging - critical for getting network details
        options.set_capability(
            "goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"}
        )

        # Initialize the driver
        self.driver = webdriver.Chrome(options=options)

    @property
    def user_agent(self):
        """
        Get the User-Agent string used by Selenium.

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
        Set the User-Agent string for Selenium.
        This is a passive operation - it only records what was passed,
        but doesn't actually modify the browser's User-Agent.

        Args:
            agent (str): The User-Agent string that was requested
        """
        # For Selenium, we just record that this was requested but don't modify
        # the browser's actual User-Agent to maintain authenticity
        print(
            f"Note: User-Agent override requested to '{agent}' but Selenium uses browser's native User-Agent"
        )

    def get(self, url, timeout=None, headers=None) -> HttpResponse:
        """
        Make a GET request using Selenium with full network information capture.

        Args:
            url (str): The URL to request
            timeout (int, optional): Request timeout in seconds
            headers (dict, optional): Additional headers (limited support)

        Returns:
            HttpResponse: Standardized response object
        """
        try:
            # Clear logs before request
            if self.driver.get_log("performance"):
                pass  # Just accessing to clear buffer

            # Note: We intentionally ignore User-Agent in headers for Selenium
            # as we want to use the browser's authentic User-Agent

            # Set page load timeout
            if timeout:
                self.driver.set_page_load_timeout(timeout)

            # Navigate to URL
            self.driver.get(url)

            # Always capture the user agent on each request
            self._user_agent = self.driver.execute_script("return navigator.userAgent;")

            # Wait for page to load (more reliable than fixed sleep)
            try:
                WebDriverWait(self.driver, timeout or 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except:
                pass  # Continue even if timeout

            # Additional wait for dynamic content if specified
            if self.wait_time:
                time.sleep(self.wait_time)

            # Get page content
            page_source = self.driver.page_source
            final_url = self.driver.current_url

            # Extract network information from performance logs
            status_code, response_headers, mime_type = self._extract_network_info(
                url, final_url
            )

            # Create comprehensive response headers
            headers = {
                "URL": final_url,
                "Content-Type": mime_type or "text/html",
                **response_headers,
            }

            # Create and return HttpResponse
            return HttpResponse(
                status_code=status_code or 200,
                text=page_source,
                headers=headers,
                content=page_source.encode("utf-8"),
            )

        except Exception as e:
            raise IOError(f"Error fetching {url} with Selenium: {e}")

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
                except:
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
                except:
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
        except:
            pass
