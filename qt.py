from ethicrawl import Ethicrawl
from ethicrawl.error import RobotDisallowedError

# Create and bind to a domain
ethicrawl = Ethicrawl()
ethicrawl.bind("https://example.com")

# Get a page - robots.txt rules automatically respected
try:
    response = ethicrawl.get("https://example.com/page.html")
except RobotDisallowedError:
    print("The site prohibits fetching the page")

# Release resources when done
ethicrawl.unbind()
