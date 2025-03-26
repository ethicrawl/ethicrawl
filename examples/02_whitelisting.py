"""
Domain whitelisting example for Ethicrawl.

This example demonstrates:
- Creating an Ethicrawl instance
- Binding to a primary website
- Attempting to access a different domain (should fail)
- Whitelisting the secondary domain
- Successfully accessing resources from the whitelisted domain
"""

from ethicrawl import Ethicrawl
from ethicrawl.error import DomainWhitelistError

# Create a new Ethicrawl instance
ethicrawl = Ethicrawl()

# Bind to the primary website
primary_site = "https://www.bbc.co.uk/"
print(f"Binding to primary site {primary_site}...")
ethicrawl.bind(primary_site)

# Define a URL from a different domain
whitelist = "https://ichef.bbci.co.uk"
image_url = f"{whitelist}/ace/standard/624/mcs/media/images/81191000/jpg/_81191156_starship2.jpg"
print(f"Image URL: {image_url}")

try:
    # First attempt to access without whitelisting (should fail)
    print("\nAttempting to access non-whitelisted domain and protocol...")
    try:
        response = ethicrawl.get(image_url)
        print("WARNING: Access should have been blocked due to domain restrictions")
    except DomainWhitelistError as e:
        print(f"Access correctly blocked (domain not whitelisted): {e}")

    # Now whitelist the secondary domain
    print("\nWhitelisting https://ichef.bbci.co.uk domain and protocol...")
    # Use the full URL form for whitelisting
    ethicrawl.whitelist(f"{whitelist}")

    # Try again (should succeed)
    print("Attempting to access image from whitelisted domain...")
    response = ethicrawl.get(image_url)
    print(
        f"Success! Image retrieved - Content type: {response.headers.get('Content-Type')}"
    )
    print(f"Image size: {len(response.content)} bytes")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Clean up
    print("\nCleaning up resources...")
    ethicrawl.unbind()
    print("Ethicrawl resources released")
