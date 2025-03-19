from unittest.mock import MagicMock, patch

from ethicrawl.config import Config
from ethicrawl.context import Context
from ethicrawl.core import Resource
from ethicrawl.client.http import HttpRequest
from ethicrawl.client.http.requests_transport import RequestsTransport


class TestRequestsTransport:
    def get_transport(self) -> RequestsTransport:
        return RequestsTransport(Context(Resource("https://www.google.com")))

    def test_user_agent(self):
        rt = self.get_transport()
        rt.user_agent = "foo"
        assert rt.user_agent == "foo"

    def test_get_request(self):
        # Create a mock response
        mock_response = MagicMock()
        mock_response.url = "https://example.com/redirected"
        mock_response.status_code = 200
        mock_response.text = "Hello, World!"
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.content = b"Hello, World!"

        # Create context and request
        context = Context(Resource("https://example.com"))
        request = HttpRequest("https://example.com", headers={"foo": "bar"})

        Config().http.proxies.http = "http://localhost:3128"
        Config().http.proxies.https = "http://localhost:3128"

        # Mock the session.get method
        with patch("requests.Session.get", return_value=mock_response):
            # Create transport with our mock
            transport = RequestsTransport(context)

            # Execute the method under test
            response = transport.get(request)

            # Assertions
            assert response.status_code == 200
            assert str(response.url) == "https://example.com/redirected"
            assert response.text == "Hello, World!"
            assert "Content-Type" in response.headers

        Config().reset()
