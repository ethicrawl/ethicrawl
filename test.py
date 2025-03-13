from ethicrawl import Ethicrawl, Config

# Configure global settings
config = Config()
config.http.rate_limit = 1.0  # 1 request per second

# Create and bind the crawler to a website
crawler = Ethicrawl()
crawler.bind("https://www.bbc.co.uk/")

# Check if a URL is allowed by robots.txt
if crawler.robots.can_fetch("https://www.bbc.co.uk/news/articles/c78e34ed111o"):
    # Fetch the page
    response = crawler.get("https://www.bbc.co.uk/news/articles/c78e34ed111o")
    print(f"Status: {response.status_code}")

# Parse sitemaps
sitemaps = crawler.robots.sitemaps
urls = crawler.sitemaps.parse(sitemaps)

# Filter URLs matching a pattern
article_urls = urls.filter(r"/news/")
print(f"Found {len(article_urls)} news URLs")

# Clean up when done
crawler.unbind()
