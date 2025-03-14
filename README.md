# Ethicrawl

[![pytest](https://github.com/ethicrawl/ethicrawl/actions/workflows/python-tests.yml/badge.svg)](https://github.com/ethicrawl/ethicrawl/actions/workflows/python-tests.yml)
[![codecov](https://codecov.io/gh/ethicrawl/ethicrawl/branch/main/graph/badge.svg)](https://codecov.io/gh/ethicrawl/ethicrawl)
[![Security](https://github.com/ethicrawl/ethicrawl/actions/workflows/security.yml/badge.svg)](https://github.com/ethicrawl/ethicrawl/actions/workflows/security.yml)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue)](https://github.com/ethicrawl/ethicrawl)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

A Python library for ethical web crawling that respects robots.txt rules, maintains proper rate limits, and provides powerful tools for web scraping.

## Features
* **Respectful by design**: Automatic robots.txt compliance and rate limiting
* **Powerful sitemap support**: Parse and filter XML sitemaps
* **Domain boundaries**: Control cross-domain access with explicit whitelisting
* **Flexible configuration**: Easily configure timeouts, rate limits, and other settings
* **Resource management**: Clean unbinding and resource release
* **JavaScript support**: Optional JavaScript rendering with Chromium

## Installation

Since this package is not yet available on PyPI, you can install it directly from GitHub:

```bash
pip install git+https://github.com/ethicrawl/ethicrawl.git
```

For development:

```bash
# Clone the repository
git clone https://github.com/ethicrawl/ethicrawl.git

# Navigate to the directory
cd ethicrawl

# Install in development mode
pip install -e .
```

## Quick Start

```python
from ethicrawl import Ethicrawl, Config

# Configure global settings
config = Config()
config.http.rate_limit = 1.0  # 1 request per second

# Create and bind the crawler to a website
crawler = Ethicrawl()
crawler.bind("https://example.com")

# Check if a URL is allowed by robots.txt
if crawler.robots.can_fetch("https://example.com/some/path"):
    # Fetch the page
    response = crawler.get("https://example.com/some/path")
    print(f"Status: {response.status_code}")

# Parse sitemaps
sitemaps = crawler.robots.sitemaps
urls = crawler.sitemaps.parse(sitemaps)

# Filter URLs matching a pattern
article_urls = urls.filter(r"/articles/")
print(f"Found {len(article_urls)} article URLs")

# Clean up when done
crawler.unbind()
```

## Responsible Web Crawling
Ethicrawl is designed to help you crawl websites responsibly:

* **Respects robots.txt rules** - Automatically checks if URLs are allowed
* **Maintains rate limits** - Prevents overloading servers with requests
* **Explicit domain boundaries** - Requires whitelisting for cross-domain requests
* **Polite bot identification** - Uses a descriptive user agent by default

## Advanced Usage
For more advanced examples, see the `usage.py` file included in the repository.

Features demonstrated in the advanced usage:

* Custom HTTP clients
* Sitemap filtering and parsing
* Domain whitelisting
* JavaScript rendering with Chromium

## Configuration
Ethicrawl provides a flexible configuration system:

```python
from ethicrawl import Config

config = Config()

# HTTP settings
config.http.timeout = 30
config.http.rate_limit = 0.5
config.http.user_agent = "MyCustomBot/1.0"

# Sitemap settings
config.sitemap.max_depth = 3

# Logging settings
config.logger.level = "INFO"
```

## License
Apache 2.0 License - See LICENSE file for details.