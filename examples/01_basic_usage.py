"""
Basic usage example for Ethicrawl library.

This example demonstrates:
- Creating an Ethicrawl instance
- Binding to a website
- Making a basic request
- Handling robots.txt restrictions
- Proper cleanup
"""

from ethicrawl import Ethicrawl
from ethicrawl.error import RobotDisallowedError

# Create a new ethicrawl instance
ethicrawl = Ethicrawl()

# Bind to a website
site = "https://www.bbc.co.uk/"
print(f"Binding to {site}...")
ethicrawl.bind(site)

# Check if we're successfully bound
if ethicrawl.bound:
    print("Crawler is bound to the BBC website")

    try:
        # Make a request to the homepage
        print(f"Requesting homepage...")
        response = ethicrawl.get(site)

        print(f"Status code: {response.status_code}")
        print(f"Content type: {response.headers.get('Content-Type')}")
        print(f"Content length: {len(response.text)}")

        # Test robots.txt compliance
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
        # Clean up
        print("\nCleaning up resources...")
        ethicrawl.unbind()
        print("Crawler resources released")
else:
    print("Failed to bind to website")
