# Documentation

We follow [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for all code documentation.

## Documentation Focus Areas

- All public APIs (methods, classes, and modules) must have comprehensive docstrings
- Private methods with complex logic should have docstrings
- Simple private methods or properties may omit docstrings
- Focus on documentation that enhances IDE tooltips and developer experience

## Docstring Format

### Module Docstrings
```python
"""Module for handling robots.txt parsing and permission checking.

This module provides functionality for fetching, parsing and checking
permissions against robots.txt files according to the Robots Exclusion
Protocol.
"""
```

### Class Docstrings
```python
class Robot:
    """Representation of a robots.txt file with permission checking.

    This class handles fetching and parsing robots.txt files and provides
    methods to check if URLs can be accessed according to the rules.

    Attributes:
        url: The URL of the robots.txt file
        sitemaps: List of sitemap URLs found in robots.txt
    """
```

### Method/Function Docstrings

```python
def can_fetch(self, url: str, user_agent: str = None) -> bool:
    """Check if a URL can be fetched according to robots.txt rules.

    Args:
        url: The URL to check against robots.txt rules
        user_agent: Optional user agent string to use for checking.
            Defaults to the client's configured user agent.

    Returns:
        True if the URL is allowed, False otherwise.

    Raises:
        RobotDisallowedError: If access is denied and raise_on_disallow=True
        ValueError: If the URL is malformed

    Example:
        >>> robot = Robot("https://example.com/robots.txt")
        >>> robot.can_fetch("https://example.com/allowed")
        True
        >>> robot.can_fetch("https://example.com/disallowed")
        False
```

### Property Docstrings

```python
@property
def sitemaps(self) -> List[str]:
    """List of sitemap URLs found in robots.txt.

    Returns:
        List of sitemap URLs as strings.
    """
```

### Constructor Docstrings

```python
def __init__(self, url: str, context: Context = None):
    """Initialize a Robot instance.

    Args:
        url: URL to the robots.txt file
        context: Optional context for the request.
            If not provided, a default context will be created.
    """
```

## Coverage Requirements

- All public methods, classes, and modules must have docstrings (100% coverage)
- Private methods with complex logic should have docstrings
- Simple private methods or properties may omit docstrings
- The overall project requires a minimum of 95% docstring coverage as measured by interrogate

## Special Cases

### Private Methods
Private methods (starting with underscore) should have docstrings if they:
- Contain complex logic
- Are called from multiple places
- Would benefit from documentation for maintainers

### One-line Docstrings

For simple methods with obvious behavior, a one-line docstring is acceptable:

```python
def is_allowed(self, url: str) -> bool:
    """Return True if the URL is allowed by robots.txt."""
```

## Verification Approach

Documentation quality is verified through code review rather than automated metrics.
Reviewers should confirm that:

- Public APIs have clear, complete docstrings
- Examples are provided for non-obvious usage
- Type information is present in docstrings
- Error cases and exceptions are documented

## Documentation Language Guidelines

When writing documentation, follow these language principles:

1. **Be objective** - Avoid subjective descriptors like "elegant", "beautiful", or "clever"
2. **Be precise** - Focus on what code does, not subjective quality judgments
3. **Be technical** - Use concrete technical terms rather than metaphorical language
4. **Be consistent** - Maintain a neutral, professional tone throughout documentation

### Examples:

Avoid:
```python
"""This elegant pattern enables seamless chaining of operations."""
```

Better:
```python
"""This design allows operation outputs to serve as inputs to other operations."""
```

Avoid
```python
"""Beautiful integration between components creates a powerful system."""
```

Better
```Components communicate through well-defined interfaces that enable extensibility.```