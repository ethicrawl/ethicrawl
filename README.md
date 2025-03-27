# Ethicrawl

[![pytest](https://github.com/ethicrawl/ethicrawl/actions/workflows/python-tests.yml/badge.svg)](https://github.com/ethicrawl/ethicrawl/actions/workflows/python-tests.yml)
[![codecov](https://codecov.io/gh/ethicrawl/ethicrawl/branch/main/graph/badge.svg)](https://codecov.io/gh/ethicrawl/ethicrawl)
[![security](https://github.com/ethicrawl/ethicrawl/actions/workflows/security.yml/badge.svg)](https://github.com/ethicrawl/ethicrawl/actions/workflows/security.yml)
[![python](https://img.shields.io/badge/python-3.10+-blue)](https://github.com/ethicrawl/ethicrawl)
[![license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/ethicrawl/ethicrawl/blob/main/LICENSE)
[![PyPI](https://badge.fury.io/py/ethicrawl.svg)](https://badge.fury.io/py/ethicrawl)
[![docs](https://img.shields.io/badge/docs-latest-blue.svg)](https://ethicrawl.github.io/ethicrawl/)

A Python library for ethical web crawling that respects robots.txt rules, maintains proper rate limits, and provides powerful tools for web scraping.

## Project Goals

Ethicrawl is built on the principle that web crawling should be:

* **Ethical**: Respect website owners' rights and server resources
* **Safe**: Prevent accidental overloading of servers or violation of policies
* **Powerful**: Provide a complete toolkit for professional web crawling
* **Extensible**: Support customization for diverse crawling needs

## Key Features

* **Robots.txt Compliance**: Automatic parsing and enforcement of robots.txt rules
* **Rate Limiting**: Built-in, configurable request rate management
* **Sitemap Support**: Parse and filter XML sitemaps to discover content
* **Domain Control**: Explicit whitelisting for cross-domain access
* **Flexible Configuration**: Easily configure all aspects of crawling behavior

## Installation

Install the latest version from PyPI:

```bash
pip install ethicrawl
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

## Documentation

Comprehensive documentation is available at [https://ethicrawl.github.io/ethicrawl/](https://ethicrawl.github.io/ethicrawl/)

## License
Apache 2.0 License - See [LICENSE](https://github.com/ethicrawl/ethicrawl/blob/main/LICENSE) file for details.