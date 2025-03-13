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

    print(f"Configuration: {config}")
    return config


def main():
    """Main demonstration function"""
    setup_logging()
    config = configure_crawler()

    print("\n==== Creating crawler and HTTP client ====")
    # Create a client with custom timeout
    client = HttpClient(timeout=20).with_chromium(headless=False)

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

"""
(venv) ➜  ethicrawl git:(develop) ✗ python usage.py
Configuration: {
  "http": {
    "headers": {},
    "jitter": 0.2,
    "max_retries": 3,
    "rate_limit": 1.0,
    "retry_delay": 1.0,
    "timeout": 15.0,
    "user_agent": "Ethicrawl/1.0"
  },
  "logger": {
    "component_levels": {},
    "console_enabled": true,
    "file_enabled": false,
    "file_path": null,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "level": 20,
    "use_colors": true
  },
  "sitemap": {
    "max_depth": 2,
    "follow_external": false,
    "validate_urls": true,
    "timeout": 30
  }
}

==== Creating crawler and HTTP client ====
Binding crawler to BBC website...

==== Checking robots.txt rules ====
2025-03-13 13:17:04,875 - ethicrawl.https_www_bbc_co_uk.robots - INFO - Fetching robots.txt: https://www.bbc.co.uk/robots.txt
2025-03-13 13:17:05,916 - ethicrawl.https_www_bbc_co_uk.robots - INFO - Successfully parsed https://www.bbc.co.uk/robots.txt
2025-03-13 13:17:05,916 - ethicrawl.https_www_bbc_co_uk.robots - INFO - Discovered 13 sitemaps in https://www.bbc.co.uk/robots.txt
Can fetch article: True
2025-03-13 13:17:05,916 - ethicrawl.https_www_bbc_co_uk.robots - WARNING - Permission check for https://www.bbc.co.uk/cbeebies/search?q=test: denied
Can fetch search: False

==== Listing sitemaps from robots.txt ====
Found 13 sitemaps:
1. https://www.bbc.co.uk/sitemap.xml
2. https://www.bbc.co.uk/sitemaps/https-index-uk-archive.xml
3. https://www.bbc.co.uk/sitemaps/https-index-uk-news.xml
4. https://www.bbc.co.uk/food/sitemap.xml
5. https://www.bbc.co.uk/bitesize/sitemap/sitemapindex.xml
6. https://www.bbc.co.uk/teach/sitemap/sitemapindex.xml
7. https://www.bbc.co.uk/sitemaps/https-index-uk-archive_video.xml
8. https://www.bbc.co.uk/sitemaps/https-index-uk-video.xml
9. https://www.bbc.co.uk/sitemaps/sitemap-uk-ws-topics.xml
10. https://www.bbc.co.uk/sport/sitemap.xml
11. https://www.bbc.co.uk/sitemaps/sitemap-uk-topics.xml
12. https://www.bbc.co.uk/ideas/sitemap.xml
13. https://www.bbc.co.uk/tiny-happy-people/sitemap/sitemapindex.xml

==== Parsing main sitemap (with depth limit) ====
Found 29348 URLs in 11.39 seconds
Found 17968 news URLs

==== Sample of news URLs ====
- https://www.bbc.co.uk/news/topics/c4y26wwj72zt
- https://www.bbc.co.uk/news/topics/czm9g685xgzt
- https://www.bbc.co.uk/news/topics/cp29jzed52et
- https://www.bbc.co.uk/news/topics/cerlz4j51w7t
- https://www.bbc.co.uk/news/topics/c27968gy256t

==== Testing domain whitelisting ====
Attempting to access image without whitelisting...
2025-03-13 13:17:17,374 - ethicrawl.https_www_bbc_co_uk - WARNING - Domain not allowed: ichef.bbci.co.uk
Expected error: Domain not allowed: ichef.bbci.co.uk

Whitelisting image domain...
2025-03-13 13:17:17,385 - ethicrawl.https_ichef_bbci_co_uk.robots - INFO - Fetching robots.txt: https://ichef.bbci.co.uk/robots.txt
2025-03-13 13:17:17,425 - ethicrawl.https_ichef_bbci_co_uk.robots - INFO - Successfully parsed https://ichef.bbci.co.uk/robots.txt
2025-03-13 13:17:17,425 - ethicrawl.https_ichef_bbci_co_uk.robots - INFO - No sitemaps found in https://ichef.bbci.co.uk/robots.txt
2025-03-13 13:17:17,425 - ethicrawl.https_www_bbc_co_uk - INFO - Whitelisted domain: ichef.bbci.co.uk
Attempting to access image after whitelisting...
Success! Got 33100 bytes of image data

==== Using Chromium for JavaScript-heavy sites ====
To use a Chromium client:
crawler.unbind()
chromium_client = client.with_chromium(headless=True)
crawler.bind('https://example.com', chromium_client)
# Now the crawler will render JavaScript before processing

==== Cleaning up ====
Crawler unbound and resources released
(venv) ➜  ethicrawl git:(develop) ✗ make test
coverage run -m pytest
======================================================================================================== test session starts =========================================================================================================
platform linux -- Python 3.10.16, pytest-8.3.5, pluggy-1.5.0
rootdir: /home/kris/code/ethicrawl
configfile: pyproject.toml
collected 125 items

tests/test_config.py ............                                                                                                                                                                                              [  9%]
tests/test_context.py .....                                                                                                                                                                                                    [ 13%]
tests/test_formatter.py .....                                                                                                                                                                                                  [ 17%]
tests/test_http_client.py ....                                                                                                                                                                                                 [ 20%]
tests/test_http_config.py ..........                                                                                                                                                                                           [ 28%]
tests/test_http_response.py ........                                                                                                                                                                                           [ 35%]
tests/test_logger_config.py ............                                                                                                                                                                                       [ 44%]
tests/test_resource.py ....                                                                                                                                                                                                    [ 48%]
tests/test_resource_list.py ....                                                                                                                                                                                               [ 51%]
tests/test_robots_handler.py .........                                                                                                                                                                                         [ 58%]
tests/test_sitemap.py .......                                                                                                                                                                                                  [ 64%]
tests/test_sitemap_entries.py .............                                                                                                                                                                                    [ 74%]
tests/test_sitemap_nodes.py ................                                                                                                                                                                                   [ 87%]
tests/test_sitemap_util.py ........                                                                                                                                                                                            [ 93%]
tests/test_url.py ........                                                                                                                                                                                                     [100%]

======================================================================================================== 125 passed in 0.43s =========================================================================================================
coverage report
Name                                     Stmts   Miss  Cover
------------------------------------------------------------
ethicrawl/__init__.py                        8      0   100%
ethicrawl/client/__init__.py                 4      0   100%
ethicrawl/client/chromium_transport.py     128    103    20%
ethicrawl/client/http_client.py             62     11    82%
ethicrawl/client/http_request.py            29     11    62%
ethicrawl/client/http_response.py           33      0   100%
ethicrawl/client/requests_transport.py      28     11    61%
ethicrawl/client/transport.py               15      4    73%
ethicrawl/config/__init__.py                 4      0   100%
ethicrawl/config/config.py                  68      6    91%
ethicrawl/config/http_config.py             80      0   100%
ethicrawl/config/logger_config.py           86      0   100%
ethicrawl/config/sitemap_config.py           7      0   100%
ethicrawl/core/__init__.py                   6      0   100%
ethicrawl/core/context.py                   40      2    95%
ethicrawl/core/ethicrawl.py                 99     61    38%
ethicrawl/core/ethicrawl_error.py            0      0   100%
ethicrawl/core/resource.py                  16      0   100%
ethicrawl/core/resource_list.py             38      3    92%
ethicrawl/core/url.py                      119     21    82%
ethicrawl/logger/__init__.py                 2      0   100%
ethicrawl/logger/formatter.py               14      0   100%
ethicrawl/logger/logger.py                  76     19    75%
ethicrawl/robots/__init__.py                 2      0   100%
ethicrawl/robots/robots_handler.py          77      3    96%
ethicrawl/sitemaps/__init__.py               3      0   100%
ethicrawl/sitemaps/sitemap_entries.py       70      0   100%
ethicrawl/sitemaps/sitemap_nodes.py         99      5    95%
ethicrawl/sitemaps/sitemap_util.py          25      0   100%
ethicrawl/sitemaps/sitemaps.py              66     54    18%
------------------------------------------------------------
TOTAL                                     1304    314    76%
"""
