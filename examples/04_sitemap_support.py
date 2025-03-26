"""
Sitemap example for Ethicrawl library.

This example demonstrates:
- Creating an Ethicrawl instance
- Binding to a website
- Finding sitemaps in robots.txt
- Parsing sitemap content
- Filtering URLs by topic
- Ethically crawling selected content
"""

from ethicrawl import Ethicrawl
from ethicrawl.sitemaps import IndexEntry, UrlsetEntry

# Create a new ethicrawl instance
ethicrawl = Ethicrawl()

# BBC website
site = "https://www.bbc.co.uk/"
print(f"Binding to {site}...")
ethicrawl.bind(site)

try:
    # First, get all sitemaps from robots.txt

    print("\nCollecting the news and sport sitemaps")
    index_entries = ethicrawl.robots.sitemaps.filter("news|sport")
    for entry in index_entries:
        index_entry: IndexEntry = entry
        print(index_entry.url)

    # pass the sitemaps we're interested in to the Sitemap Parser
    urlset_entries = ethicrawl.sitemaps.parse(index_entries)
    print(f"Found {len(urlset_entries)} urls:")

    print("\nExample UrlsetEntry from sitemap:")
    for i, resource in enumerate(urlset_entries[:5], 1):
        urlset_entry: UrlsetEntry = resource
        print(f"  {i}. {urlset_entry.url} | {urlset_entry.lastmod}")


except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Clean up resources
    print("\nCleaning up resources...")
    ethicrawl.unbind()
    print("Ethicrawl resources released")
