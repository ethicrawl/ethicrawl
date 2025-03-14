"""
Ethicrawl Usage Example

This script demonstrates how to use the Ethicrawl library for ethical
web crawling that respects robots.txt rules and maintains proper rate limits.
"""

from ethicrawl import Ethicrawl, HttpClient, Url, Resource, ResourceList, Config
import time
import re
import logging
import sys


def setup_logging():
    """Configure logging for the demo"""
    # Configure root logger to show INFO and above
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def configure_crawler():
    """Setup custom configuration"""
    config = Config()

    # HTTP settings
    config.http.timeout = 15
    config.http.rate_limit = 1.0  # 1 request per second max
    config.http.jitter = 0.2  # Add up to 20% random delay

    # Sitemap settings
    config.sitemap.max_depth = 2  # Limit sitemap recursion

    # Logging settings
    config.logger.level = "INFO"

    # Proxy settings
    # config.http.set_all_proxies("http://localhost:3128")

    print(f"Configuration: {config}")
    return config


def main():
    """Main demonstration function"""
    setup_logging()
    config = configure_crawler()

    print("\n==== Creating crawler and HTTP client ====")

    # Create a client with custom timeout
    client = HttpClient(timeout=20)  # .with_chromium(headless=False)

    # Create and bind the crawler
    crawler = Ethicrawl()
    print("Binding crawler to BBC website...")
    crawler.bind("https://www.bbc.co.uk/", client)

    print("\n==== Checking robots.txt rules ====")
    # Check if certain paths are allowed
    article_url = "https://www.bbc.co.uk/news/uk-northern-ireland-31591567"
    print(f"Can fetch article: {crawler.robots.can_fetch(article_url)}")

    search_url = "https://www.bbc.co.uk/cbeebies/search?q=test"
    print(f"Can fetch search: {crawler.robots.can_fetch(search_url)}")

    # Get all the sitemaps from robots.txt
    print("\n==== Listing sitemaps from robots.txt ====")
    sitemap_urls = crawler.robots.sitemaps
    print(f"Found {len(sitemap_urls)} sitemaps:")
    for i, url in enumerate(sitemap_urls, 1):
        print(f"{i}. {url}")

    # Process just the main sitemap with depth limit
    print("\n==== Parsing main sitemap (with depth limit) ====")
    # Filter to just the main sitemap
    main_sitemap = crawler.robots.sitemaps.filter(r"https://www.bbc.co.uk/sitemap.xml")

    start_time = time.time()
    urls = crawler.sitemaps.parse(main_sitemap)
    duration = time.time() - start_time

    print(f"Found {len(urls)} URLs in {duration:.2f} seconds")

    # Filter URLs by pattern
    news_urls = urls.filter(r"/news/")
    print(f"Found {len(news_urls)} news URLs")

    # Show a sample of news URLs
    print("\n==== Sample of news URLs ====")
    for url in news_urls[:5]:  # Show first 5 news URLs
        print(f"- {url.url}")

    # Try to access an image URL from a different domain
    print("\n==== Testing domain whitelisting ====")
    image_url = "https://ichef.bbci.co.uk/ace/standard/624/mcs/media/images/81191000/jpg/_81191156_starship2.jpg"

    try:
        print("Attempting to access image without whitelisting...")
        response = crawler.get(image_url)
    except ValueError as e:
        print(f"Expected error: {e}")

    # Now whitelist the image domain and try again
    print("\nWhitelisting image domain...")
    crawler.whitelist("https://ichef.bbci.co.uk")

    try:
        print("Attempting to access image after whitelisting...")
        response = crawler.get(image_url)
        print(f"Success! Got {len(response.content)} bytes of image data")
    except Exception as e:
        print(f"Error: {e}")

    # Show how to use a Chromium client for JavaScript-heavy sites
    print("\n==== Using Chromium for JavaScript-heavy sites ====")
    print("To use a Chromium client:")
    print("crawler.unbind()")
    print("chromium_client = client.with_chromium(headless=True)")
    print("crawler.bind('https://example.com', chromium_client)")
    print("# Now the crawler will render JavaScript before processing")

    # Clean up
    print("\n==== Cleaning up ====")
    crawler.unbind()
    print("Crawler unbound and resources released")


if __name__ == "__main__":
    main()
