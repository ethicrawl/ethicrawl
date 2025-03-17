# User Guide

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

## Basic Use

```python
from ethicrawl import Ethicrawl

# create an ethicrawl instance
ec = Ethicrawl()

# bind the instance to a website
ec.bind("https://www.bbc.co.uk/")

# get a page - the first request will fetch robots.txt and discover sitemaps if they exist
response = ec.get("https://www.bbc.co.uk/news/uk-northern-ireland-31591567")

print(response.headers["Content-Type"])
print(len(response.text))

# text/html
# 311550

# try to fetch a page forbidden by robots.txt
try:
    response = ec.get("https://www.bbc.co.uk/userinfo")
except ValueError as e:
    print(e)  # URL disallowed by robots.txt: https://www.bbc.co.uk/userinfo

# load an image from the page
try:
    response = ec.get(
        "https://ichef.bbci.co.uk/ace/standard/624/mcs/media/images/81191000/jpg/_81191156_starship2.jpg.webp"
    )
except ValueError as e:
    print(e)  # Domain not allowed: ichef.bbci.co.uk

# whitelist the additional domain and get the image again. each whitelisted domain is subject to its own robots.txt file

ec.whitelist("https://ichef.bbci.co.uk")
response = ec.get(
    "https://ichef.bbci.co.uk/ace/standard/624/mcs/media/images/81191000/jpg/_81191156_starship2.jpg.webp"
)

print(response.headers["Content-Type"])
print(len(response.content))

# image/webp
# 16994

# finally unbind from the website to clear the connection and any whitelists
ec.unbind()

```

## Clients

## Logging

## Configuration

## Caching and Proxies

## Robots

## Sitemaps