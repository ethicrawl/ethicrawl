"""
Resources and ResourceLists example for Ethicrawl library.

This example demonstrates:
- Creating Resource objects from URLs
- Building ResourceLists of different types
- Adding and removing Resources from lists
- Filtering ResourceLists with patterns
- Using ResourceLists with Ethicrawl operations
- Type safety and specialized Resource subclasses
"""

from ethicrawl import Ethicrawl
from ethicrawl.core import Resource, ResourceList, Url
from ethicrawl.sitemaps import SitemapEntry, UrlsetEntry

# Create Resource objects - the fundamental unit of Ethicrawl
print("Creating basic Resources...")
resource1 = Resource("https://example.com/page1")
resource2 = Resource("https://example.com/page2?q=test")
resource3 = Resource(Url("https://example.com/blog/article"))

# Print resource information
print(f"Resource 1: {resource1}")
print(f"Resource 2: {resource2}")
print(f"Resource 3: {resource3}")
print(f"Resource identity check (1 == 2): {resource1 == resource2}")
print(
    f"Resource identity check (1 == 1): {resource1 == Resource('https://example.com/page1')}"
)

# Create a ResourceList and add resources
print("\nBuilding ResourceLists...")
resource_list = ResourceList()
resource_list.append(resource1)
resource_list.append(resource2)
resource_list.append(resource3)

# You can also create with initial items
initial_list = ResourceList(
    [
        Resource("https://example.com/products/1"),
        Resource("https://example.com/products/2"),
    ]
)

# ResourceLists support common operations
print(f"List length: {len(resource_list)}")
print(f"First resource: {resource_list[0]}")
print(f"Sliced list (first 2): {resource_list[:2]}")

# Filtering ResourceLists
print("\nFiltering ResourceLists...")
# Filter for pages with 'page' in the URL
page_resources = resource_list.filter("page")
print(f"Resources with 'page' in URL: {len(page_resources)}")
for resource in page_resources:
    print(f"  - {resource}")

# Filter for blog articles
blog_resources = resource_list.filter("blog|article")
print(f"Resources with 'blog' or 'article' in URL: {len(blog_resources)}")
for resource in blog_resources:
    print(f"  - {resource}")

# Working with specialized Resource types
print("\nSpecialized Resource types...")
# SitemapEntry extends Resource with sitemap-specific fields
sitemap_entry = SitemapEntry(
    Url("https://example.com/sitemap.xml"), lastmod="2025-03-26T12:00:00Z"
)
print(f"Sitemap entry: {sitemap_entry}")

# Combining with Ethicrawl operations
print("\nUsing ResourceLists with Ethicrawl...")
try:
    ethicrawl = Ethicrawl()
    ethicrawl.bind("https://example.com")

    # Create a filtered list of resources to fetch
    fetch_list = ResourceList(
        [
            Resource("https://example.com/page1"),
            Resource("https://example.com/page2"),
            Resource("https://example.com/page3"),
        ]
    )

    # Filter to just pages 1 and 2
    filtered_list = fetch_list.filter("page[12]")
    print(f"Will fetch {len(filtered_list)} resources:")
    for resource in filtered_list:
        print(f"  - {resource}")

    # You would typically fetch these in a real application
    # for resource in filtered_list:
    #    response = ethicrawl.get(resource)
    #    process_response(response)

except Exception as e:
    print(f"Error: {e}")
finally:
    if "ethicrawl" in locals() and ethicrawl.bound:
        ethicrawl.unbind()
