#!/usr/bin/env python3

import http.server
import socketserver
import os
import logging
import argparse
from typing import Dict, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ethicrawl-test-server")


class EthicrawlTestHandler(http.server.SimpleHTTPRequestHandler):
    # Root directory to serve files from
    root_directory = "htdocs"

    # Content type mappings for our specific files
    content_types = {
        ".xml": "application/xml",
        ".txt": "text/plain",
        ".html": "text/html",
    }

    def __init__(self, *args, **kwargs):
        # Set directory to htdocs
        super().__init__(*args, directory=self.root_directory, **kwargs)

    def log_message(self, format, *args):
        """Override to use our logger instead of default print to stderr"""
        logger.info(f"{self.address_string()} - {format%args}")

    def guess_type(self, path):
        """Override the mime type guesser for specific file extensions"""
        # Extract extension from path
        ext = os.path.splitext(path)[1].lower()
        if ext in self.content_types:
            return self.content_types[ext]
        # Fall back to default implementation
        return super().guess_type(path)


def run_server(port: int = 8000, bind: str = ""):
    """Run the HTTP server on the specified port"""
    handler = EthicrawlTestHandler

    with socketserver.TCPServer((bind, port), handler) as httpd:
        host = bind if bind else "localhost"
        logger.info(f"Starting ethicrawl test server at http://{host}:{port}/")
        logger.info(f"Serving files from '{os.path.abspath(handler.root_directory)}'")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Shutting down server...")
        finally:
            httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a simple HTTP server for ethicrawl testing"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)",
    )
    parser.add_argument(
        "--bind",
        type=str,
        default="",
        help="Address to bind to (default: all interfaces)",
    )

    args = parser.parse_args()
    run_server(port=args.port, bind=args.bind)
