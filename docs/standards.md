# Coding Standards

## Python Code Standards

### General Requirements
- **Python Version**: We target Python 3.10 and above
  - Code may work on earlier versions but is not tested or supported
- **Line Endings**: Use UNIX-style line endings (LF, `\n`)
- **Indentation**: Use 4 spaces for indentation (no tabs)
- **Maximum Line Length**: 88 characters (Black default)

### Code Formatting

We use [Black](https://github.com/psf/black) as our code formatter with default settings:

```shell
# Install Black
pip install black

# Format a single file
black path/to/file.py

# Format all Python files in a directory
black directory_name/
```
### Import Organization
Imports should be grouped in the following order, with a blank line between each group:

* Standard library imports
* Third-party imports
* Local application imports

```python
# Standard library
import os
from datetime import datetime

# Third-party
import requests
from bs4 import BeautifulSoup

# Local
from ethicrawl.core import Resource
from ethicrawl.config import Config
```

### Type Hints

Use type hints for all public methods and functions:

```python
def process_url(url: str, timeout: Optional[int] = None) -> Dict[str, Any]:
    """Process the given URL and return results."""
```


##### Method/Function Docstrings
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
    """
```


## Error Handling Style Guide for Ethicrawl
A consistent approach to error handling improves code readability and helps developers understand and handle errors effectively. This document outlines our standards for raising exceptions in the Ethicrawl codebase.

### General Principles
1. Be specific - Use the most specific exception type appropriate for the error
2. Be descriptive - Error messages should help users identify and fix problems
3. Be consistent - Follow the same patterns throughout the codebase

### Standard Exception Types

#### TypeError
Use for incorrect argument types or invalid operations on types.

##### Format:
```python
raise TypeError(f"Expected {expected_type}, got {type(actual).__name__}")
```

##### Examples:

```python
raise TypeError(f"Expected string, Url, or Resource, got {type(resource).__name__}")
raise TypeError("headers must be a Headers instance or dictionary")
```

#### ValueError
Use for arguments that have the right type but an invalid value.

##### Format:

```python
raise ValueError(f"{parameter_name} must be {constraint}")
```

##### Examples:

```python
raise ValueError("jitter must be between 0.0 and 1.0")
raise ValueError("max_retries cannot be negative")
```

### Domain-Specific Exceptions
Create custom exceptions for domain-specific errors. All custom exceptions should:

1. Inherit from appropriate base exceptions
2. Include "Error" in the class name
3. Be placed in a relevant _error.py module

##### Example:

```python
class RobotDisallowedError(ValueError):
    """Raised when access to a URL is disallowed by robots.txt rules."""
```

### Error Message Guidelines

1. Be specific about what went wrong
2. Provide the invalid value when helpful
3. Suggest a fix when possible
4. Use consistent terminology across similar errors

### Documenting Exceptions

```python
def function_name():
    """Function description.

    Args:
        param_name: Parameter description.

    Returns:
        Return description.

    Raises:
        ExceptionType: Condition when raised.
        AnotherException: Another condition.
    """
```

Always document exceptions in docstrings:

### Error Assertions
For internal logic verification, use assertions with descriptive messages:

```python
assert isinstance(item, Resource), f"Expected Resource, got {type(item).__name__}"
```


## Documentation

We follow [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for all code documentation.

### Documentation Focus Areas

- All public APIs (methods, classes, and modules) must have comprehensive docstrings
- Private methods with complex logic should have docstrings
- Simple private methods or properties may omit docstrings
- Focus on documentation that enhances IDE tooltips and developer experience

### Docstring Format

#### Module Docstrings
```python
"""Module for handling robots.txt parsing and permission checking.

This module provides functionality for fetching, parsing and checking
permissions against robots.txt files according to the Robots Exclusion
Protocol.
"""
```

#### Class Docstrings
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

#### Method/Function Docstrings

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

#### Property Docstrings

```python
@property
def sitemaps(self) -> List[str]:
    """List of sitemap URLs found in robots.txt.

    Returns:
        List of sitemap URLs as strings.
    """
```

#### Constructor Docstrings

```python
def __init__(self, url: str, context: Context = None):
    """Initialize a Robot instance.

    Args:
        url: URL to the robots.txt file
        context: Optional context for the request.
            If not provided, a default context will be created.
    """
```

### Coverage Requirements

- All public methods, classes, and modules must have docstrings (100% coverage)
- Private methods with complex logic should have docstrings
- Simple private methods or properties may omit docstrings
- The overall project requires a minimum of 95% docstring coverage as measured by interrogate

### Special Cases

#### Private Methods
Private methods (starting with underscore) should have docstrings if they:
- Contain complex logic
- Are called from multiple places
- Would benefit from documentation for maintainers

#### One-line Docstrings

For simple methods with obvious behavior, a one-line docstring is acceptable:

```python
def is_allowed(self, url: str) -> bool:
    """Return True if the URL is allowed by robots.txt."""
```

### Verification Approach

Documentation quality is verified through code review rather than automated metrics.
Reviewers should confirm that:

- Public APIs have clear, complete docstrings
- Examples are provided for non-obvious usage
- Type information is present in docstrings
- Error cases and exceptions are documented

### Documentation Language Guidelines

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

## Logging Standards for Ethicrawl

Good logging practices are essential for troubleshooting, monitoring, and understanding application behavior.

### Log Levels and Their Uses

#### CRITICAL (logging.CRITICAL, 50)
Use for severe errors that prevent core functionality from working.

##### When to use:

* Application cannot continue functioning
* Data corruption or loss has occurred
* Security breaches or compromises
* Resource exhaustion that threatens system stability

##### Examples:

```python
logger.critical(f"Failed to initialize client: {error}")
logger.critical(f"Persistent storage corruption detected in {file_path}")
```
#### ERROR (logging.ERROR, 40)

Use for runtime errors that prevent specific operations from completing but don't crash the application.

##### When to use:

* Failed HTTP requests
* Failed data processing operations
* Configuration errors
* External service unavailability
* Unexpected exceptions in non-critical paths

#### Examples:

```python
logger.error(f"HTTP request failed: {status_code} {reason}")
logger.error(f"Failed to parse sitemap at {url}: {error_message}")
```

#### WARNING (logging.WARNING, 30)

Use for conditions that might cause problems but allow operations to continue.

#### When to use:

* Deprecated feature usage
* Slow response times
* Retrying operations after recoverable failures
* Access denied for certain operations
* Unexpected data formats that can be handled
* Rate limiting being applied

##### Examples:

```python
logger.warning(f"URL disallowed by robots.txt: {url}")
logger.warning(f"Slow response from {domain}: {response_time}s")
logger.warning(f"Retrying request ({retry_count}/{max_retries})")
```

#### INFO (logging.INFO, 20)

Use for normal operational events and milestones.

##### When to use:

* Application startup and shutdown
* Configuration settings
* Successful site binding and crawling
* Processing milestones
* Summary information about operations
* Changes to application state

##### Examples:

```python
logger.info(f"Bound to site: {url}")
logger.info(f"Robots.txt processed: {allowed_count} allowed paths, {disallowed_count} disallowed")
logger.info(f"Processed {page_count} pages in {duration}s")
```

#### DEBUG (logging.DEBUG, 10)

Use for detailed information useful during development and debugging.

##### When to use:

* Function entry/exit points
* Variable values and state changes
* Decision logic paths
* Low-level HTTP details
* Parsing steps
* Rate limiting details

##### Examples:

```python
logger.debug(f"Processing URL: {url}")
logger.debug(f"Page found in cache, age: {cache_age}s")
logger.debug(f"Parser state: {current_state}")
```

#### Logging Best Practices
1. Be Concise and Specific
* Include exactly what happened and where
* Use active voice (e.g., "Failed to connect" instead of "Connection failure occurred")

2. Include Context
* Always include relevant identifiers (URLs, IDs, component names)
* Include relevant variable values
* For errors, include exception messages and/or stack traces

3. Be Consistent
* Use consistent terminology across similar log messages
* Use consistent formatting for similar events
* Use sentence case for log messages (capitalize first word)

4. Avoid Sensitive Information
* No authentication credentials
* No personal data
* No sensitive headers or tokens

5. Use Structured Fields for Machine Parsing
* Place structured data at the end of the message
* Use consistent key-value format: `key=value`

#### Component-Specific Guidelines

Each component should have a consistent logging identity:

1. Robot/Robots.txt
* INFO: Robots.txt fetching and parsing results
* WARNING: Disallowed access attempts
* ERROR: Failed to fetch/parse robots.txt

2. HTTP Client
* DEBUG: Request details
* INFO: Rate limiting information
* WARNING: Retries and slow responses
* ERROR: Failed requests

3. Sitemap
* INFO: Sitemap discovery and parsing
* WARNING: Malformed but recoverable sitemap content
* ERROR: Failed sitemap fetching/parsing
