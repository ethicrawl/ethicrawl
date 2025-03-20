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
### Documentation

* All modules, classes, methods, and functions should have docstrings
* Use Google-style docstrings with type information
* Include example usage for public APIs when appropriate

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

By following these guidelines, we'll maintain a consistent approach to error handling across the Ethicrawl codebase.

## Logging Standards for Ethicrawl

Good logging practices are essential for troubleshooting, monitoring, and understanding application behavior. This document outlines our logging standards for the Ethicrawl codebase.

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

By following these guidelines, we'll maintain a consistent and helpful logging strategy across the Ethicrawl codebase.
