from ethicrawl import EthiCrawl
from ethicrawl.client import HttpClient
from ethicrawl.sitemaps import SitemapFactory

if __name__ == "__main__":
    ethicrawl = EthiCrawl(
        "https://gb.maxmara.com/", http_client=HttpClient.with_selenium(headless=False)
    )
    print(ethicrawl._sitemaps.items)

# https://gb.maxmara.com/
# Fetching robots.txt: https://gb.maxmara.com/robots.txt
# Successfully parsed robots.txt
# Found 2 sitemaps in robots.txt
#   - https://gb.maxmara.com/sitemap.xml
#   - https://gb.maxmara.com/v/nc/sitemap/sitemap.xml
# [SitemapIndexUrl(loc='https://gb.maxmara.com/sitemap.xml', lastmod='2025-03-01'), SitemapIndexUrl(loc='https://gb.maxmara.com/v/nc/sitemap/sitemap.xml', lastmod='2025-03-01')]
