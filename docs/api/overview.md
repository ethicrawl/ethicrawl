# Overview

Ethicrawl is organized into several key modules:

- **Ethicrawl**: Provides the main interface for operating with the library.

- **Core**: Fundamental components including URL handling, resource management, and standardized data structures. Provides the `Resource`, `ResourceList`, and `Url` classes that are the building blocks of crawling operations.

- **Client**: HTTP clients for various access methods:
  - **HttpClient**: Standard requests-based client for most web resources
  - **ChromeClient**: Browser automation for JavaScript-heavy sites using Selenium

- **Context**: Manages the crawling environment including domain boundaries, allowed paths, and session state. Enforces ethical boundaries during execution.

- **Sitemaps**: Tools for parsing and utilizing XML sitemaps. Provides classes for handling `IndexEntry`, `UrlsetEntry`, and other sitemap standard formats.

- **Robots**: Robots.txt parsing and rule enforcement. Ensures crawlers respect website policies regarding crawlable content.

- **Config**: Configuration management for controlling crawler behavior. Provides a singleton `Config` class for global settings and per-instance overrides.

- **Logger**: Customizable logging functionality with sensible defaults for tracking crawler operations.

- **Error**: Specialized exception classes for error handling, including `DomainWhitelistError`, `RobotDisallowedError`, and other ethical boundary violations.

## Getting Started

The typical usage flow follows this pattern:

1. Create an `Ethicrawl` instance
2. Bind to a primary domain
3. Access content with the built-in HTTP methods

```python
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
```

For detailed usage examples, see the examples directory in the repository.