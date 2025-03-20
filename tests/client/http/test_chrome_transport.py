# Here be dragons

import pytest
import json
from unittest.mock import Mock, patch

from ethicrawl.config import Config
from ethicrawl.context import Context
from ethicrawl.core import Resource, Url
from ethicrawl.client.http import HttpRequest
from ethicrawl.client.http.chrome_transport import ChromeTransport


@pytest.fixture
def mock_webdriver():
    mock_driver = Mock()

    # Set up properties and methods
    mock_driver.page_source = "<html><body>Test content</body></html>"
    mock_driver.current_url = "https://example.com/result"

    # Mock get_log to return realistic performance logs
    mock_driver.get_log.return_value = [
        {
            "message": json.dumps(
                {
                    "message": {
                        "method": "Network.responseReceived",
                        "params": {
                            "response": {
                                "url": "https://example.com",
                                "status": 200,
                                "headers": {"Content-Type": "text/html"},
                                "mimeType": "text/html",
                            },
                            "type": "Document",
                        },
                    }
                }
            )
        }
    ]

    # Mock execute_script for user agent retrieval
    mock_driver.execute_script.return_value = "Mozilla/5.0 (Test) Chrome/Test"

    return mock_driver


class TestChromeTransport:
    def test_extract_xml_content(self):
        """Test XML content extraction from Chrome-rendered XML"""
        url = "https://www.example.com"
        context = Context(Resource(Url(url)))
        transport = ChromeTransport(context)

        # Test with normal HTML content
        html_content = "<html><body>Test</body></html>"
        result = transport._extract_xml_content(html_content)
        assert result == html_content.encode("utf-8")

        # Test with Chrome-rendered XML content
        xml_viewer_html = """<html>
            <div id="webkit-xml-viewer-source-xml">
                <item>Value</item>
            </div>
        </html>"""
        result = transport._extract_xml_content(xml_viewer_html)
        assert b"<item>Value</item>" in result

    def test_get_xml_content(self, mock_webdriver):
        """Test XML content extraction during GET requests"""
        url = "https://www.example.com/feed.xml"
        context = Context(Resource(Url(url)))

        # Set up our mocked webdriver with XML viewer content
        xml_viewer_html = """<html>
            <div id="webkit-xml-viewer-source-xml">
                <item>XML Content</item>
            </div>
        </html>"""
        mock_webdriver.page_source = xml_viewer_html
        mock_webdriver.current_url = url

        with (
            patch("selenium.webdriver.Chrome", return_value=mock_webdriver),
            patch("selenium.webdriver.support.ui.WebDriverWait"),
            patch("ethicrawl.client.http.chrome_transport.sleep"),
        ):

            transport = ChromeTransport(context)
            transport.driver = mock_webdriver

            # Create request object for XML URL
            request = HttpRequest(url=Url(url))

            # Mock response info to indicate XML content
            with patch.object(
                transport,
                "_get_response_information",
                return_value=(200, {}, "application/xml"),
            ):

                # Execute get request
                response = transport.get(request)

                # Verify XML extraction occurred
                assert "<item>XML Content</item>" in response.text
                assert response.headers["Content-Type"] == "application/xml"

    @patch("selenium.webdriver.Chrome")
    def test_chrome_transport_init(self, mock_chrome_class):
        """Test ChromeTransport initialization"""
        mock_driver = Mock()
        mock_chrome_class.return_value = mock_driver

        url = "https://www.example.com"
        context = Context(Resource(Url(url)))
        transport = ChromeTransport(context)

        # Just verify Chrome was instantiated with options
        mock_chrome_class.assert_called_once()

        # Check options were passed
        options_arg = mock_chrome_class.call_args[1].get("options")
        assert options_arg is not None

        # Verify driver was assigned
        assert transport.driver is mock_driver

    def test_get_response_information(self, mock_webdriver):
        """Test extraction of network information from performance logs"""
        url = "https://www.example.com"
        context = Context(Resource(Url(url)))

        with patch("selenium.webdriver.Chrome", return_value=mock_webdriver):
            transport = ChromeTransport(context)
            transport.driver = mock_webdriver

            status_code, headers, mime_type = transport._get_response_information(
                "https://example.com", "https://example.com/result"
            )

            assert status_code == 200
            assert headers == {"Content-Type": "text/html"}
            assert mime_type == "text/html"

    def test_get_method_with_headers(self, mock_webdriver):
        """Test GET request with headers (which Chrome can't fully support)"""
        url = "https://www.example.com"
        context = Context(Resource(Url(url)))

        # Set up our mocked webdriver
        mock_webdriver.page_source = "<html><body>Test content</body></html>"
        mock_webdriver.current_url = url

        with (
            patch("selenium.webdriver.Chrome", return_value=mock_webdriver),
            patch("selenium.webdriver.support.ui.WebDriverWait"),
            patch("ethicrawl.client.http.chrome_transport.sleep"),
        ):

            transport = ChromeTransport(context)
            transport.driver = mock_webdriver

            # Create request with custom headers
            custom_headers = {
                "User-Agent": "Custom/1.0",
                "Accept": "text/html",
                "X-Custom-Header": "test-value",
            }
            request = HttpRequest(url=Url(url), headers=custom_headers)

            # Mock the logger to verify debug message
            with patch.object(transport._logger, "debug") as mock_debug:
                # Mock response info
                with patch.object(
                    transport,
                    "_get_response_information",
                    return_value=(200, {}, "text/html"),
                ):

                    # Execute the request
                    response = transport.get(request)

                    # Verify debug message was logged about headers
                    headers_call = [
                        call
                        for call in mock_debug.call_args_list
                        if "Headers requested" in str(call)
                    ]
                    assert len(headers_call) == 1
                    assert "User-Agent" in str(headers_call[0])
                    assert "Accept" in str(headers_call[0])
                    assert "X-Custom-Header" in str(headers_call[0])

                    # Verify request was still made successfully
                    mock_webdriver.get.assert_called_once_with(url)
                    assert response.status_code == 200

    def test_get_response_information_document_fallback(self, mock_webdriver):
        """Test document type response fallback when no exact URL match is found"""
        url = "https://www.example.com"
        context = Context(Resource(Url(url)))

        # Create mock logs where no entry matches the requested URL exactly,
        # but there is a Document type response we can fall back to
        mock_webdriver.get_log.return_value = [
            # Non-matching URL response (but Document type)
            {
                "message": json.dumps(
                    {
                        "message": {
                            "method": "Network.responseReceived",
                            "params": {
                                "type": "Document",
                                "response": {
                                    "url": "https://example.com/page",  # Different URL
                                    "status": 200,
                                    "headers": {"Content-Type": "text/html"},
                                    "mimeType": "text/html",
                                },
                            },
                        }
                    }
                )
            },
            # Some other resource like an image
            {
                "message": json.dumps(
                    {
                        "message": {
                            "method": "Network.responseReceived",
                            "params": {
                                "type": "Image",
                                "response": {
                                    "url": "https://example.com/image.png",
                                    "status": 200,
                                    "headers": {"Content-Type": "image/png"},
                                    "mimeType": "image/png",
                                },
                            },
                        }
                    }
                )
            },
        ]

        with patch("selenium.webdriver.Chrome", return_value=mock_webdriver):
            transport = ChromeTransport(context)
            transport.driver = mock_webdriver

            # Call _get_response_information with URLs that won't match any response
            status_code, headers, mime_type = transport._get_response_information(
                "https://example.com/not-matching", "https://example.com/not-matching"
            )

            # Should fall back to the Document type response
            assert status_code == 200
            assert headers == {"Content-Type": "text/html"}
            assert mime_type == "text/html"

            # Verify log was accessed
            mock_webdriver.get_log.assert_called_once_with("performance")

    def test_get_response_information_default_fallback(self, mock_webdriver):
        """Test default fallback when no matching response or Document type is found"""
        url = "https://www.example.com"
        context = Context(Resource(Url(url)))

        # Mock logs with entries that won't match our criteria
        mock_webdriver.get_log.return_value = [
            # Image type response (not a Document)
            {
                "message": json.dumps(
                    {
                        "message": {
                            "method": "Network.responseReceived",
                            "params": {
                                "type": "Image",
                                "response": {
                                    "url": "https://example.com/image.png",
                                    "status": 200,
                                    "headers": {"Content-Type": "image/png"},
                                    "mimeType": "image/png",
                                },
                            },
                        }
                    }
                )
            },
            # Font type resource (not a Document)
            {
                "message": json.dumps(
                    {
                        "message": {
                            "method": "Network.responseReceived",
                            "params": {
                                "type": "Font",
                                "response": {
                                    "url": "https://example.com/font.woff2",
                                    "status": 200,
                                    "headers": {"Content-Type": "font/woff2"},
                                    "mimeType": "font/woff2",
                                },
                            },
                        }
                    }
                )
            },
            # Not even a response entry
            {
                "message": json.dumps(
                    {"message": {"method": "Network.requestWillBeSent", "params": {}}}
                )
            },
        ]

        with patch("selenium.webdriver.Chrome", return_value=mock_webdriver):
            transport = ChromeTransport(context)
            transport.driver = mock_webdriver

            # Call with URLs that won't match any response
            status_code, headers, mime_type = transport._get_response_information(
                "https://example.com/not-matching", "https://example.com/not-matching"
            )

            # Should return default values
            assert status_code == 200  # Default status
            assert headers == {}  # Default empty headers
            assert mime_type == "text/html"  # Default MIME type

            # Verify log was accessed
            mock_webdriver.get_log.assert_called_once_with("performance")

    @pytest.mark.parametrize(
        "http_proxy,https_proxy,expected_calls",
        [
            # Case 1: Different proxies
            (
                "127.0.0.1:8080",
                "localhost:8443",
                [
                    "--proxy-server=http=127.0.0.1:8080",
                    "--proxy-server=https=localhost:8443",
                ],
            ),
            # Case 2: Same proxy for both HTTP and HTTPS
            (
                "proxy.example.com:8080",
                "proxy.example.com:8080",
                ["--proxy-server=proxy.example.com:8080"],
            ),
        ],
    )
    def test_proxy_configuration(self, http_proxy, https_proxy, expected_calls):
        """Test proxy configuration is applied correctly"""
        url = "https://www.example.com"
        context = Context(Resource(Url(url)))

        # Create a patch stack to control all dependencies
        with patch(
            "ethicrawl.client.http.chrome_transport.Config"
        ) as mock_config_class:
            # Set up the full object chain
            mock_config = Mock()
            mock_config_class.return_value = mock_config

            mock_http = Mock()
            mock_config.http = mock_http

            mock_proxies = Mock()
            mock_http.proxies = mock_proxies

            # Set the proxy values
            mock_proxies.http = http_proxy
            mock_proxies.https = https_proxy

            # Also mock Chrome and Options
            with patch("selenium.webdriver.Chrome") as mock_chrome_class:
                with patch(
                    "ethicrawl.client.http.chrome_transport.Options"
                ) as mock_options_class:
                    mock_options = Mock()
                    mock_options_class.return_value = mock_options

                    mock_driver = Mock()
                    mock_chrome_class.return_value = mock_driver

                    # Create the transport
                    transport = ChromeTransport(context)

                    # Verify each expected call was made
                    for arg in expected_calls:
                        mock_options.add_argument.assert_any_call(arg)

    def test_user_agent_getter_setter(self, mock_webdriver):
        """Test user_agent property getter and setter"""
        url = "https://www.example.com"
        context = Context(Resource(Url(url)))

        with patch("selenium.webdriver.Chrome", return_value=mock_webdriver):
            transport = ChromeTransport(context)

            # Test initial getter (should fetch from browser)
            expected_ua = "Mozilla/5.0 (Test) Chrome/Test"
            mock_webdriver.execute_script.return_value = expected_ua

            # First call should navigate to about:blank
            ua = transport.user_agent
            mock_webdriver.get.assert_called_with("about:blank")
            assert ua == expected_ua

            # Second call should use cached value (no additional browser calls)
            mock_webdriver.reset_mock()
            ua2 = transport.user_agent
            mock_webdriver.get.assert_not_called()
            assert ua2 == expected_ua

            # Test error handling path
            mock_webdriver.reset_mock()
            mock_webdriver.execute_script.side_effect = Exception("Test error")
            transport._user_agent = None  # Clear cached value

            # Should return fallback UA on error
            ua3 = transport.user_agent
            assert "Unknown" in ua3

            # Test setter (doesn't actually change browser UA)
            with patch.object(transport._logger, "debug") as mock_debug:
                transport.user_agent = "Custom/1.0"
                mock_debug.assert_called_once()
                assert "User-Agent override requested" in mock_debug.call_args[0][0]

    def test_extract_response_info_from_log_entry(self):
        """Test extracting response info from performance log entries"""
        url = "https://www.example.com"
        context = Context(Resource(Url(url)))
        transport = ChromeTransport(context)

        # Test 1: Valid log entry
        valid_entry = {
            "message": json.dumps(
                {
                    "message": {
                        "method": "Network.responseReceived",
                        "params": {
                            "response": {
                                "url": "https://example.com",
                                "status": 200,
                                "headers": {"Content-Type": "text/html"},
                            }
                        },
                    }
                }
            )
        }

        params, response = transport._extract_response_info_from_log_entry(valid_entry)
        assert params is not None
        assert response is not None
        assert response["url"] == "https://example.com"

        # Test 2: Non-Network.responseReceived entry
        other_entry = {
            "message": json.dumps(
                {"message": {"method": "Network.requestWillBeSent", "params": {}}}
            )
        }

        result = transport._extract_response_info_from_log_entry(other_entry)
        assert result is None

        # Test 3: Malformed entry
        malformed_entry = {"message": "not json"}
        result = transport._extract_response_info_from_log_entry(malformed_entry)
        assert result is None

    def test_extract_response_info_from_response(self):
        """Test extracting status, headers and MIME from response dict"""
        url = "https://www.example.com"
        context = Context(Resource(Url(url)))
        transport = ChromeTransport(context)

        # Test 1: Complete response
        full_response = {
            "status": 200,
            "mimeType": "text/html",
            "headers": {"Content-Type": "text/html", "Server": "nginx"},
        }

        status, headers, mime = transport._extract_response_info_from_response(
            full_response
        )
        assert status == 200
        assert mime == "text/html"
        assert headers["Content-Type"] == "text/html"
        assert headers["Server"] == "nginx"

        # Test 2: Partial response
        partial_response = {"status": 404, "headers": {}}  # No MIME type

        status, headers, mime = transport._extract_response_info_from_response(
            partial_response
        )
        assert status == 404
        assert mime is None
        assert headers == {}

        # Test 3: Error case
        with patch.object(transport._logger, "debug") as mock_debug:
            status, headers, mime = transport._extract_response_info_from_response(None)
            assert status is None
            assert headers == {}
            assert mime is None
            mock_debug.assert_called_once()
