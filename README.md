# Ethicrawl

[![python](https://img.shields.io/badge/python-3.10+-blue)](https://github.com/ethicrawl/ethicrawl)
[![license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/ethicrawl/ethicrawl/blob/main/LICENSE)
[![pytest](https://github.com/ethicrawl/ethicrawl/actions/workflows/python-tests.yml/badge.svg)](https://github.com/ethicrawl/ethicrawl/actions/workflows/python-tests.yml)
[![codecov](https://codecov.io/gh/ethicrawl/ethicrawl/branch/main/graph/badge.svg)](https://codecov.io/gh/ethicrawl/ethicrawl)
[![security](https://github.com/ethicrawl/ethicrawl/actions/workflows/security.yml/badge.svg)](https://github.com/ethicrawl/ethicrawl/actions/workflows/security.yml)
[![PyPI](https://badge.fury.io/py/ethicrawl.svg)](https://badge.fury.io/py/ethicrawl)
[![docs](https://img.shields.io/badge/docs-latest-blue.svg)](https://ethicrawl.github.io/ethicrawl/)

Ethicrawl is a Python library for ethical, professional-grade web crawling. It automatically respects robots.txt, enforces rate limits, and offers robust sitemap parsing and domain control—making it easy to build reliable and responsible crawlers.

## Project Goals

Ethicrawl is built on the principle that web crawling should be:

* **Ethical by Design**: Automatically respects robots.txt and rate limits, ensuring responsible web crawling.
* **Server-Safe**: Prevents accidental overloading with built-in safeguards.
* **Feature-Rich**: Includes robust sitemap parsing, domain control, and flexible configuration.
* **Extensible & Customizable**: Easily adapts to diverse crawling needs through flexible settings and clean architecture.

## Key Features

* **Robots.txt Compliance**: Automatic parsing and enforcement of robots.txt rules
* **Rate Limiting**: Built-in, configurable request rate management
* **Sitemap Support**: Parse and filter XML sitemaps to discover content
* **Domain Control**: Explicit whitelisting for cross-domain access
* **Flexible Configuration**: Easily configure all aspects of crawling behavior

## Documentation

Comprehensive documentation is available at [https://ethicrawl.github.io/ethicrawl/](https://ethicrawl.github.io/ethicrawl/)

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

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

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
    response = ethicrawl.get("https://example.com/page.html")
except RobotDisallowedError:
    print("The site prohibits fetching the page")

# Release resources when done
ethicrawl.unbind()
```

## License
Apache 2.0 License - See [LICENSE](https://github.com/ethicrawl/ethicrawl/blob/main/LICENSE) file for details.