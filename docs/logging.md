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
