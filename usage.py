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
    client = HttpClient(timeout=20).with_chrome(headless=False)

    # Create and bind the crawler
    crawler = Ethicrawl()
    print("Binding crawler to BBC website...")
    crawler.bind("https://www.bbc.co.uk/", client)

    print("\n==== Checking robots.txt rules ====")
    # Check if certain paths are allowed
    article_url = "https://www.bbc.co.uk/news/uk-northern-ireland-31591567"
    print(f"Can fetch article: {crawler.robots.can_fetch(article_url)}")

    try:
        search_url = "https://www.bbc.co.uk/cbeebies/search?q=test"
        print(f"Can fetch search: {crawler.robots.can_fetch(search_url)}")
    except Exception as e:
        print((f"Can fetch search: {search_url}"), e)

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

# (venv) ➜  ethicrawl git:(optional) ✗ python usage.py
# Configuration: {
#   "http": {
#     "timeout": 15.0,
#     "rate_limit": 1.0,
#     "jitter": 0.2,
#     "max_retries": 3,
#     "retry_delay": 1.0,
#     "user_agent": "Ethicrawl/1.0",
#     "headers": {},
#     "proxies": {
#       "http": null,
#       "https": null
#     }
#   },
#   "logger": {
#     "level": 20,
#     "console_enabled": true,
#     "file_enabled": false,
#     "file_path": null,
#     "use_colors": true,
#     "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     "component_levels": {}
#   },
#   "sitemap": {
#     "max_depth": 2,
#     "follow_external": false,
#     "validate_urls": true
#   }
# }

# ==== Creating crawler and HTTP client ====
# Binding crawler to BBC website...

# ==== Checking robots.txt rules ====
# 2025-03-20 18:32:27,782 - ethicrawl.https_www_bbc_co_uk.robots - INFO - Server returned 200 - using robots.txt
# Can fetch article: True
# 2025-03-20 18:32:33,009 - ethicrawl.https_www_bbc_co_uk.robots - INFO - Server returned 200 - using robots.txt
# 2025-03-20 18:32:33,010 - ethicrawl.https_www_bbc_co_uk.robots - WARNING - Permission check for https://www.bbc.co.uk/cbeebies/search?q=test with User-Agent 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36': denied
# Can fetch search: https://www.bbc.co.uk/cbeebies/search?q=test Permission denied by robots.txt for User-Agent 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36' at URL 'https://www.bbc.co.uk/cbeebies/search?q=test'

# ==== Listing sitemaps from robots.txt ====
# 2025-03-20 18:32:38,156 - ethicrawl.https_www_bbc_co_uk.robots - INFO - Server returned 200 - using robots.txt
# Found 13 sitemaps:
# 1. https://www.bbc.co.uk/sitemap.xml
# 2. https://www.bbc.co.uk/sitemaps/https-index-uk-archive.xml
# 3. https://www.bbc.co.uk/sitemaps/https-index-uk-news.xml
# 4. https://www.bbc.co.uk/food/sitemap.xml
# 5. https://www.bbc.co.uk/bitesize/sitemap/sitemapindex.xml
# 6. https://www.bbc.co.uk/teach/sitemap/sitemapindex.xml
# 7. https://www.bbc.co.uk/sitemaps/https-index-uk-archive_video.xml
# 8. https://www.bbc.co.uk/sitemaps/https-index-uk-video.xml
# 9. https://www.bbc.co.uk/sitemaps/sitemap-uk-ws-topics.xml
# 10. https://www.bbc.co.uk/sport/sitemap.xml
# 11. https://www.bbc.co.uk/sitemaps/sitemap-uk-topics.xml
# 12. https://www.bbc.co.uk/ideas/sitemap.xml
# 13. https://www.bbc.co.uk/tiny-happy-people/sitemap/sitemapindex.xml

# ==== Parsing main sitemap (with depth limit) ====
# 2025-03-20 18:32:43,404 - ethicrawl.https_www_bbc_co_uk.robots - INFO - Server returned 200 - using robots.txt
# Found 29354 URLs in 46.66 seconds
# Found 17968 news URLs

# ==== Sample of news URLs ====
# - https://www.bbc.co.uk/news/topics/c4y26wwj72zt
# - https://www.bbc.co.uk/news/topics/czm9g685xgzt
# - https://www.bbc.co.uk/news/topics/cp29jzed52et
# - https://www.bbc.co.uk/news/topics/cerlz4j51w7t
# - https://www.bbc.co.uk/news/topics/c27968gy256t

# ==== Testing domain whitelisting ====
# Attempting to access image without whitelisting...
# 2025-03-20 18:33:30,128 - ethicrawl.https_www_bbc_co_uk - WARNING - Domain not allowed: ichef.bbci.co.uk
# Expected error: Domain not allowed: ichef.bbci.co.uk

# Whitelisting image domain...
# 2025-03-20 18:33:34,500 - ethicrawl.https_ichef_bbci_co_uk.robots - INFO - Server returned 200 - using robots.txt
# 2025-03-20 18:33:34,500 - ethicrawl.https_www_bbc_co_uk - INFO - Whitelisted domain: ichef.bbci.co.uk
# Attempting to access image after whitelisting...
# Success! Got 489 bytes of image data

# ==== Using Chromium for JavaScript-heavy sites ====
# To use a Chromium client:
# crawler.unbind()
# chromium_client = client.with_chromium(headless=True)
# crawler.bind('https://example.com', chromium_client)
# # Now the crawler will render JavaScript before processing

# ==== Cleaning up ====
# Crawler unbound and resources released
