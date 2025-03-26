"""
Chrome client example for Ethicrawl library.

This example demonstrates:
- Creating an Ethicrawl instance with Chrome browser
- Binding to a website
- Making a request that fully renders JavaScript
- Handling robots.txt restrictions
- Proper cleanup of browser resources
"""

from ethicrawl import Ethicrawl
from ethicrawl.client.http import HttpClient
from ethicrawl.error import RobotDisallowedError

# Create a Chrome client
client = HttpClient().with_chrome(
    headless=False,  # Run Chrome without visible window
    timeout=30,  # Wait up to 30 seconds for page loads
)

# Create a new ethicrawl instance
ethicrawl = Ethicrawl()

# Bind to a website with custom client
site = "https://www.bbc.co.uk/"
print(f"Binding to {site} with Chrome browser...")
ethicrawl.bind(site, client=client)

# Check if we're successfully bound
if ethicrawl.bound:
    print("Ethicrawl is bound to the BBC website using Chrome")

    try:
        # Make a request to the homepage - now with full JavaScript rendering
        print(f"Requesting homepage (with JavaScript rendering)...")
        response = ethicrawl.get(site)

        print(f"Status code: {response.status_code}")
        print(f"Content type: {response.headers.get('Content-Type')}")
        print(f"Content length: {len(response.text)}")

        # Access JavaScript-rendered content
        print("\nAccessing dynamically loaded content...")
        if "BBC" in response.text:
            print("Successfully rendered JavaScript content")

        # Test robots.txt compliance (still works with Chrome client)
        print("\nTesting robots.txt compliance...")
        url = site + "search/"
        print(f"Attempting to access {url} (disallowed in robots.txt)")

        try:
            ethicrawl.get(url)
            print("WARNING: Access should have been blocked by robots.txt")
        except RobotDisallowedError as e:
            print(f"Access correctly blocked by robots.txt: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Clean up (will close Chrome browser)
        print("\nCleaning up resources...")
        ethicrawl.unbind()
        print("Ethicrawl resources released")
else:
    print("Failed to bind to website")
