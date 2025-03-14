import pytest
from unittest.mock import patch, MagicMock, call
import json

from ethicrawl.client.chromium_transport import ChromiumTransport
from ethicrawl.client.http_request import HttpRequest
from ethicrawl.core.context import Context
from ethicrawl.core.url import Url
from ethicrawl.core.resource import Resource


class TestChromiumTransport:
    @patch("ethicrawl.client.chromium_transport.webdriver")
    def setup_method(self, _, mock_webdriver):
        """Set up test fixtures."""
        # Create mocks
        self.mock_driver = MagicMock()
        mock_webdriver.Chrome.return_value = self.mock_driver

        # Setup mock response for user agent
        self.mock_driver.execute_script.return_value = "Mozilla/5.0 Mock Chrome"

        # Create a context
        self.resource = Resource("https://example.com")
        self.mock_client = MagicMock()
        with patch("ethicrawl.core.context.isinstance", return_value=True):
            self.context = Context(self.resource, self.mock_client)

        # Create the transport
        self.transport = ChromiumTransport(self.context)

    def test_initialization(self):
        """Test initialization of ChromiumTransport."""
        # Verify Chrome was initialized with correct options
        from selenium.webdriver.chrome.options import Options

        with patch(
            "ethicrawl.client.chromium_transport.Options", return_value=MagicMock()
        ) as mock_options:
            with patch(
                "ethicrawl.client.chromium_transport.webdriver"
            ) as mock_webdriver:
                # Create transport
                transport = ChromiumTransport(self.context)

                # Verify options were set
                assert mock_options.return_value.add_argument.call_count >= 4
                mock_options.return_value.add_argument.assert_any_call("--headless")
                mock_options.return_value.add_argument.assert_any_call("--no-sandbox")

                # Verify webdriver was initialized
                mock_webdriver.Chrome.assert_called_once()

    def test_user_agent_getter_cached(self):
        """Test user_agent property returns cached value if available."""
        # Set a cached value
        self.transport._user_agent = "Cached Agent"

        # Get the user agent
        result = self.transport.user_agent

        # Verify the cached value was returned
        assert result == "Cached Agent"
        # Verify no browser interactions happened
        self.mock_driver.get.assert_not_called()

    def test_user_agent_getter_not_cached(self):
        """Test user_agent property fetches from browser if not cached."""
        # Clear cached value
        self.transport._user_agent = None

        # Set expected return from browser
        self.mock_driver.execute_script.return_value = "Fresh User Agent"

        # Get the user agent
        result = self.transport.user_agent

        # Verify browser was used to get value
        self.mock_driver.get.assert_called_once_with("about:blank")
        self.mock_driver.execute_script.assert_called_once()
        assert result == "Fresh User Agent"

    def test_user_agent_getter_exception(self):
        """Test user_agent property handles errors."""
        # Clear cached value
        self.transport._user_agent = None

        # Make the browser throw an exception
        self.mock_driver.execute_script.side_effect = Exception("Browser error")

        # Get the user agent
        result = self.transport.user_agent

        # Verify we got a default value
        assert "Mozilla/5.0" in result
        assert "Unknown" in result

    @patch("builtins.print")
    def test_user_agent_setter(self, mock_print):
        """Test user_agent setter behavior."""
        # Set a user agent
        self.transport.user_agent = "Custom Agent"

        # Verify it wasn't actually set but was logged
        mock_print.assert_called_once()
        assert "User-Agent override requested" in mock_print.call_args[0][0]

    @patch("ethicrawl.client.chromium_transport.WebDriverWait")
    @patch("ethicrawl.client.chromium_transport.time")
    def test_get_successful(self, mock_time, mock_wait):
        """Test successful GET request."""
        # Set up request
        request = HttpRequest(Url("https://example.com/test"))

        # Mock driver response
        self.mock_driver.page_source = "<html><body>Test Page</body></html>"
        self.mock_driver.current_url = "https://example.com/test"

        # Need to mock HttpResponse construction
        with patch(
            "ethicrawl.client.chromium_transport.HttpResponse"
        ) as mock_http_response:
            mock_response = MagicMock()
            mock_http_response.return_value = mock_response

            # Mock network info extraction
            with patch.object(
                self.transport,
                "_extract_network_info",
                return_value=(200, {"Server": "mock"}, "text/html"),
            ):
                # Make request
                response = self.transport.get(request)

                # Verify driver was used correctly
                self.mock_driver.get.assert_called_once_with("https://example.com/test")
                self.mock_driver.set_page_load_timeout.assert_called_once()
                mock_time.sleep.assert_called_once()

                # Verify HttpResponse was created with correct parameters
                mock_http_response.assert_called_once()
                call_args, call_kwargs = mock_http_response.call_args

                # Check if request is passed as positional argument
                if call_args and len(call_args) > 0:
                    assert call_args[0] == request
                # Or as keyword argument
                else:
                    assert call_kwargs.get("request") == request

                assert call_kwargs.get("status_code") == 200
                assert "Server" in call_kwargs.get("headers", {})

                # Verify return value
                assert response == mock_response

    def test_get_exception(self):
        """Test GET request handling exceptions."""
        # Set up request
        request = HttpRequest(Url("https://example.com/error"))

        # Make driver throw exception
        self.mock_driver.get.side_effect = Exception("Browser error")

        # Verify exception is wrapped
        with pytest.raises(IOError) as exc_info:
            self.transport.get(request)

        assert "Error fetching" in str(exc_info.value)
        assert "Browser error" in str(exc_info.value)

    def test_extract_xml_content_standard(self):
        """Test XML content extraction for standard content."""
        content = "<html><body>Regular HTML</body></html>"
        result = self.transport._extract_xml_content(content)

        # Should return original content encoded
        assert result == content.encode("utf-8")

    def test_extract_xml_content_from_viewer(self):
        """Test XML content extraction from Chrome XML viewer."""
        # Mock Chrome's XML viewer HTML
        viewer_html = """
        <html>
            <div id="webkit-xml-viewer-source-xml">
                <foo>Test XML content</foo>
                <bar attr="value">More content</bar>
            </div>
        </html>
        """

        with patch(
            "ethicrawl.client.chromium_transport.html.fromstring"
        ) as mock_fromstring:
            # Set up mock XML elements
            mock_foo = MagicMock()
            mock_bar = MagicMock()
            mock_div = MagicMock()

            mock_div.getchildren.return_value = [mock_foo, mock_bar]
            mock_foo_str = b"<foo>Test XML content</foo>"
            mock_bar_str = b'<bar attr="value">More content</bar>'

            # Setup fromstring to return a mock document
            mock_fromstring.return_value = MagicMock()
            mock_fromstring.return_value.xpath.return_value = [mock_div]

            # Mock lxml.etree.tostring
            with patch(
                "ethicrawl.client.chromium_transport.lxml.etree.tostring"
            ) as mock_tostring:
                mock_tostring.side_effect = lambda x, encoding: (
                    mock_foo_str.decode() if x is mock_foo else mock_bar_str.decode()
                )

                result = self.transport._extract_xml_content(viewer_html)

                # Should contain both XML elements
                assert b"<foo>Test XML content</foo>" in result
                assert b"<bar" in result

    def test_extract_network_info_exact_match(self):
        """Test extracting network info with exact URL match."""
        # Mock requested and final URL
        req_url = "https://example.com/test"
        final_url = "https://example.com/test"

        # Create mock log entries
        log_entries = [
            {
                "message": json.dumps(
                    {
                        "message": {
                            "method": "Network.responseReceived",
                            "params": {
                                "response": {
                                    "url": req_url,
                                    "status": 200,
                                    "mimeType": "text/html",
                                    "headers": {
                                        "Content-Type": "text/html",
                                        "Server": "nginx",
                                    },
                                }
                            },
                        }
                    }
                )
            },
            {"message": json.dumps({"message": {"method": "Network.someOtherEvent"}})},
        ]

        self.mock_driver.get_log.return_value = log_entries

        # Call the method
        status, headers, mime = self.transport._extract_network_info(req_url, final_url)

        # Verify correct values extracted
        assert status == 200
        assert mime == "text/html"
        assert headers["Server"] == "nginx"
        assert headers["Content-Type"] == "text/html"

    def test_extract_network_info_document_type(self):
        """Test extracting network info by document type when URL doesn't match."""
        # Mock requested and final URL
        req_url = "https://example.com/original"
        final_url = "https://example.com/redirected"

        # Create mock log entries with no exact match but a Document type
        log_entries = [
            {
                "message": json.dumps(
                    {
                        "message": {
                            "method": "Network.responseReceived",
                            "params": {
                                "type": "Document",
                                "response": {
                                    "url": "https://example.com/different",
                                    "status": 200,
                                    "mimeType": "text/html",
                                    "headers": {
                                        "Content-Type": "text/html",
                                        "Server": "nginx",
                                    },
                                },
                            },
                        }
                    }
                )
            }
        ]

        self.mock_driver.get_log.return_value = log_entries

        # Call the method
        status, headers, mime = self.transport._extract_network_info(req_url, final_url)

        # Verify correct values extracted
        assert status == 200
        assert mime == "text/html"
        assert headers["Server"] == "nginx"

    def test_extract_network_info_no_match(self):
        """Test extracting network info with no matches."""
        # Mock empty logs
        self.mock_driver.get_log.return_value = []

        # Call the method
        status, headers, mime = self.transport._extract_network_info("url", "final_url")

        # Verify default values
        assert status is None
        assert headers == {}
        assert mime is None

    @patch("builtins.print")
    def test_extract_network_info_exception(self, mock_print):
        """Test extracting network info with exception."""
        # Make get_log throw exception
        self.mock_driver.get_log.side_effect = Exception("Log error")

        # Call the method
        status, headers, mime = self.transport._extract_network_info("url", "final_url")

        # Verify error was logged and defaults returned
        mock_print.assert_called_once()
        assert "Error extracting network info" in mock_print.call_args[0][0]
        assert status is None
        assert headers == {}
        assert mime is None

    @patch("builtins.hasattr")
    def test_del_cleanup(self, mock_hasattr):
        """Test __del__ cleanup."""
        # Make hasattr return True
        mock_hasattr.return_value = True

        # Call __del__
        self.transport.__del__()

        # Verify driver was quit
        self.mock_driver.quit.assert_called_once()

    @patch("builtins.hasattr")
    def test_del_exception(self, mock_hasattr):
        """Test __del__ with exception."""
        # Make hasattr return True but quit throw exception
        mock_hasattr.return_value = True
        self.mock_driver.quit.side_effect = Exception("Quit error")

        # Call __del__ - should not raise exception
        self.transport.__del__()
