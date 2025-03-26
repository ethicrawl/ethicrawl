"""
Proxies and Caching example for Ethicrawl library.

This example demonstrates:
- Configuring Ethicrawl to use a proxy server (Squid)
- Making requests through the proxy
- Understanding the benefits of proxies for ethical crawling
"""

import json
import time
from ethicrawl import Ethicrawl
from ethicrawl.config import Config

# Define proxy configuration
PROXY_URL = "http://localhost:3128"  # Squid proxy running on localhost

# Method 1: Configure proxies globally through Config singleton
print("Configuring proxy using Config() singleton...")
Config().http.proxies.http = PROXY_URL
Config().http.proxies.https = PROXY_URL

# Create Ethicrawl instance (will use proxy from Config)
ethicrawl = Ethicrawl()
print("Ethicrawl instance created with proxy configuration")

# Target a test endpoint
site = "https://httpbin.org/get"
print(f"Binding to {site}...")
ethicrawl.bind(site)

try:
    # Make a request through the proxy
    print("\nMaking request through proxy...")
    start_time = time.time()
    response = ethicrawl.get(site)
    elapsed = time.time() - start_time

    print(f"Response status: {response.status_code}")
    print(f"Time taken: {elapsed:.2f} seconds")

    # Look for evidence of proxy use in response data
    print("\nResponse data (showing proxy is being used):")
    if "application/json" in response.headers.get("content-type", ""):
        # Parse the JSON response body
        json_data = json.loads(response.content)

        # Show the origin IP (this is how we know the proxy is working)
        if "origin" in json_data:
            print(f"Request came from IP: {json_data['origin']}")

        # Show headers that were sent through the proxy
        if "headers" in json_data:
            print("Headers sent through proxy:")
            for key, value in json_data["headers"].items():
                print(f"  {key}: {value}")

            # Note about missing Via header
            if "Via" not in json_data["headers"]:
                print(
                    "\nNote: 'Via' header is not present, but the request is still going through the proxy"
                )
                print(
                    "      as evidenced by the origin IP. You can enable Via headers in squid.conf with:"
                )
                print("      via on")

    # Benefits section
    print("\nBenefits of using a proxy for crawling:")
    print("1. Reduced load on target servers (caching)")
    print("2. Rate limiting and request throttling")
    print("3. IP rotation for reducing impact on target servers")
    print("4. Normalized request headers for consistent crawling")
    print("5. Tracking and auditing capabilities")


except Exception as e:
    print(f"Error: {e}")

finally:
    # Clean up resources
    print("\nCleaning up resources...")
    ethicrawl.unbind()
    print("Ethicrawl resources released")
