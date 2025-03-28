"""
Proxies and Caching example for Ethicrawl library.

To use this example, you need a proxy available.

docker run -d --name squid-container -e TZ=UTC -p 3128:3128 ubuntu/squid:5.2-22.04_beta

This example demonstrates:
- Configuring Ethicrawl to use a proxy server (Squid)
- Making requests through the proxy
- Understanding the benefits of proxies for ethical crawling
"""

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
site = "https://httpbin.org/headers?show_env"
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
