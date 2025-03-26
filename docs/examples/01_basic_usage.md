# Basic Usage

This guide demonstrates the fundamental operations with Ethicrawl: creating a crawler, binding to a site, making requests, and cleaning up resources.

## Creating an Ethicrawl Instance

First, import the main `Ethicrawl` class and create an instance:

```python
from ethicrawl import Ethicrawl

# Create a new crawler instance
crawler = Ethicrawl()
```

## Binding to a Website

```markdown
# Basic Usage

This guide demonstrates the fundamental operations with Ethicrawl: creating a crawler, binding to a site, making requests, and cleaning up resources.

## Creating an Ethicrawl Instance

First, import the main `Ethicrawl` class and create an instance:

```python
from ethicrawl import Ethicrawl

# Create a new crawler instance
ethicrawl = Ethicrawl()
```

## Binding to a Website

Before making requests, you must bind ethicrawl to a website. This establishes the domain context:

```python
# Bind to a website
site = "https://www.bbc.co.uk/"
ethicrawl.bind(site)

# Check if we're successfully bound
if ethicrawl.bound:
    print("Crawler is bound to the BBC website")
```

## Make a request to the homepage

```python
response = ethicrawl.get(site)

print(f"Status code: {response.status_code}")
print(f"Content type: {response.headers.get('Content-Type')}")
print(f"Content length: {len(response.text)}")
```

## Robots support

The BBC website has an exclusion rule for search;

`Disallow: /search/`

```python
from ethicrawl.error import RobotsDisallowedError

url = site + "/search/"

try:
    ethicrawl.get(url)
except RobotsDisallowedError:
    print(f"The url f{url} was disallowed by robots.txt")
```

## Cleanup

Unbind to the website when you are finished with it, this will release all resources.

```python

ethicrawl.unbind()

```
