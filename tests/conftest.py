import pytest
import socket
import threading
from flask import Flask, Response
import time


from ethicrawl.config import Config
from ethicrawl.logger import Logger


def _fake_gethostbyname(hostname: str) -> str:
    """Offline stand-in for socket.gethostbyname.

    Fully-qualified names (anything with a dot) and ``localhost`` resolve to
    the loopback address; bare single-label names fail, mirroring what a real
    resolver does for something like ``http://x``.
    """
    if hostname == "localhost" or "." in hostname:
        return "127.0.0.1"
    raise socket.gaierror(socket.EAI_NONAME, "Name or service not known")


@pytest.fixture(autouse=True)
def offline_dns(monkeypatch):
    """Keep the suite hermetic: Url(validate=True) must not hit real DNS."""
    monkeypatch.setattr("ethicrawl.core.url.gethostbyname", _fake_gethostbyname)


@pytest.fixture(autouse=True)
def reset_all_singletons():
    """Reset all singleton classes before and after each test."""
    # Reset before test
    Config().reset()
    Logger().reset()

    # Run the test
    yield

    # Reset after test
    Config().reset()
    Logger().reset()


@pytest.fixture(scope="session")
def test_server():
    """Fixture that runs a local Flask server for testing"""
    app = Flask("test_server")

    @app.route("/robots.txt")
    def robots():
        return Response(
            "User-agent: *\n"
            "Allow: /\n\n"
            "User-agent: BadBot\n"
            "Disallow: /private/\n\n"
            "Sitemap: http://localhost:5000/sitemap.xml",
            mimetype="text/plain",
        )

    @app.route("/sitemap.xml")
    def sitemap():
        return Response(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            "</sitemapindex>",
            mimetype="application/xml",
        )

    @app.route("/")
    def index():
        return "<html><body>Home page</body></html>"

    @app.route("/<path:page>")
    def page(page):
        return f"<html><body>Page: {page}</body></html>"

    # Start server in a thread
    server_thread = threading.Thread(
        target=lambda: app.run(port=5000, use_reloader=False)
    )
    server_thread.daemon = True  # Ensure thread doesn't block test exit
    server_thread.start()

    # Wait for server to start
    time.sleep(0.5)

    yield "http://localhost:5000"
