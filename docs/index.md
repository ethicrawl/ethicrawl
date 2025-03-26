# Ethicrawl Documentation

Welcome to Ethicrawl, a Python library designed for ethical and respectful web crawling. Ethicrawl provides tools and abstractions to help developers build crawlers that follow best practices, respect site policies, and minimize server impact.

## Overview

Ethicrawl focuses on:

- **Ethical Crawling**: Respectful of robots.txt, rate limits, and server resources
- **Resource Abstractions**: Type-safe handling of web resources and collections
- **Policy Enforcement**: Automatic compliance with web standards
- **Comprehensive Logging**: Detailed visibility into crawler operations
- **Configurability**: Fine-grained control over crawler behavior

## Getting Started

### Installation

```bash
pip install ethicrawl
```

### Basic Usage

```python
from ethicrawl import Ethicrawl
from ethicrawl.error import RobotDisallowedError

# Create and bind to a domain
ethicrawl = Ethicrawl()
ethicrawl.bind("https://example.com")

# Get a page - robots.txt rules automatically respected
try:
    response = ethicrawl.get("/page.html")
except RobotDisallowedError:
    print("The site prohibits fetching the page")

# Release resources when done
ethicrawl.unbind()
```

## Examples

Our examples directory contains practical demonstrations of Ethicrawl's features:

1. **[Basic Usage](/examples/01_basic_usage.py)**: Simple crawling with automatic robots.txt compliance
2. **[Domain Whitelisting](/examples/02_whitelisting.py)**: Allowing access to secondary domains
3. **[Chrome Client](/examples/03_chrome_client.py)**: Using Chrome browser for JavaScript rendering
4. **[Sitemap Support](/examples/04_sitemap_support.py)**: Parsing and using sitemaps
5. **[Resources and ResourceLists](/examples/05_resources_and_resource_lists.py)**: Working with web resources
6. **[Proxies and Caching](/examples/06_proxies_and_caching.py)**: Using proxy servers
7. **[Configuration](/examples/07_config.py)**: Configuring Ethicrawl
8. **[Logging](/examples/08_logging.py)**: Using the logging system

## API Reference

- **[Ethicrawl](/docs/ethicrawl/ethicrawl.html)**: Main class and package documentation
- **[Core](/docs/ethicrawl/core/index.html)**: Resource, ResourceList, Url, and other fundamental abstractions
- **[Context](/docs/ethicrawl/context/index.html)**: Context management for crawling operations
- **[Client](/docs/ethicrawl/client/index.html)**: HTTP and Chrome client implementations
- **[Config](/docs/ethicrawl/config/index.html)**: Configuration system and singleton
- **[Robots](/docs/ethicrawl/robots/index.html)**: Robots.txt parsing and enforcement
- **[Sitemaps](/docs/ethicrawl/sitemaps/index.html)**: Sitemap parsing and URL extraction
- **[Logger](/docs/ethicrawl/logger/index.html)**: Logging system and hierarchical loggers

## Documentation Guides

- **[Standards](/docs/standards.md)**: Coding standards and style guide for Ethicrawl development
- **[Logging](/docs/logging.md)**: Detailed guide to Ethicrawl's logging system
- **[Documentation](/docs/documentation.md)**: Guidelines for contributing to these docs


## Project Structure

```
ethicrawl/
├── core/         # Core abstractions (Resource, Url, etc.)
├── context/      # Context passed around within the system
├── client/       # Client implementations
├── config/       # Configuration system
├── robots/       # Robots.txt parser and enforcer
├── sitemaps/     # Sitemap parser
└── logger/       # Logging system
```
