# Coding Standards and Contributing

## Error Handling Style Guide for Ethicrawl
A consistent approach to error handling improves code readability and helps developers understand and handle errors effectively. This document outlines our standards for raising exceptions in the Ethicrawl codebase.

## General Principles
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