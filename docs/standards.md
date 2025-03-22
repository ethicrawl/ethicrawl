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

