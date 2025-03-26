"""
Logging System example for Ethicrawl library.

This example demonstrates:
- Creating and configuring loggers
- Component-specific logging
- Resource-specific logging
- Logging configuration through the Config system
- Console and file output options
- Hierarchical logging structure
"""

import logging
import os
from ethicrawl import Ethicrawl
from ethicrawl.config import Config
from ethicrawl.core import Resource, Url
from ethicrawl.logger import Logger

# 1. CONFIGURING THE LOGGING SYSTEM
print("==== CONFIGURING THE LOGGING SYSTEM ====")

# Access the global configuration singleton
config = Config()

# Show default logging configuration
print("\nDefault Logger Configuration:")
print(f"Level: {logging.getLevelName(config.logger.level)}")
print(f"Console Enabled: {config.logger.console_enabled}")
print(f"File Enabled: {config.logger.file_enabled}")
print(f"File Path: {config.logger.file_path or 'None'}")
print(f"Use Colors: {config.logger.use_colors}")

# Customize logging configuration
print("\nCustomizing logging configuration...")
config.logger.level = "DEBUG"  # Set global level to DEBUG
config.logger.use_colors = True  # Enable colored console output

# Enable file logging
log_file = "ethicrawl_example.log"
config.logger.file_enabled = True
config.logger.file_path = log_file
print(f"Enabled file logging to: {log_file}")

# Set component-specific log levels
config.logger.set_component_level("robots", "DEBUG")  # Detailed robots logs
config.logger.set_component_level("http", "WARNING")  # Reduced HTTP noise
config.logger.set_component_level("sitemaps", "INFO")  # Standard sitemap logs

# 2. GETTING AND USING LOGGERS
print("\n==== WORKING WITH LOGGERS ====")

# Create resources
example_com = Resource("https://example.com")
api_example = Resource("https://api.example.com")

# Get different types of loggers
print("\nCreating resource-specific loggers...")

# Resource-specific loggers (all loggers must be tied to a resource)
example_logger = Logger.logger(example_com)
api_logger = Logger.logger(api_example)
print(f"Resource logger names:")
print(f"  - {example_logger.name}")
print(f"  - {api_logger.name}")

# Component-specific resource loggers
robots_logger = Logger.logger(example_com, "robots")
http_logger = Logger.logger(example_com, "http")
sitemap_logger = Logger.logger(api_example, "sitemaps")

print(f"Component logger names:")
print(f"  - {robots_logger.name}")
print(f"  - {http_logger.name}")
print(f"  - {sitemap_logger.name}")

# 3. LOGGING AT DIFFERENT LEVELS

# Component loggers with different levels
robots_logger.debug("Parsing robots.txt rules")  # Will appear (DEBUG level)
http_logger.debug("Making HTTP request")  # Won't appear (WARNING level)
http_logger.warning("Slow response time")  # Will appear (WARNING level)
sitemap_logger.debug("Processing sitemap XML")  # Won't appear (INFO level)
sitemap_logger.info("Found 10 URLs in sitemap")  # Will appear (INFO level)

# 4. LOGGER HIERARCHY
print("\n==== LOGGER HIERARCHY ====")
print("Ethicrawl uses a hierarchical logger structure:")
print("- ethicrawl (root)")
print("  - ethicrawl.example_com (resource)")
print("    - ethicrawl.example_com.robots (component)")
print("    - ethicrawl.example_com.http (component)")
print("  - ethicrawl.api_example_com (resource)")
print("    - ethicrawl.api_example_com.sitemaps (component)")

# 5. PRACTICAL USAGE WITH ETHICRAWL
print("\n==== PRACTICAL LOGGING WITH ETHICRAWL ====")
print("When using Ethicrawl, loggers are created automatically:")

try:
    # Create a crawler instance
    crawler = Ethicrawl()
    crawler.bind("https://httpbin.org")

    # Crawl a page (will generate log messages)
    print("\nMaking a request that will generate log messages...")
    crawler.get("/get")

    # By default, Ethicrawl uses hierarchical loggers:
    # - ethicrawl.https_httpbin_org (bound domain)
    # - ethicrawl.https_httpbin_org.robots (robots.txt component)
    # - ethicrawl.https_httpbin_org.http (HTTP client component)

except Exception as e:
    print(f"Error: {e}")
finally:
    if "crawler" in locals() and crawler.bound:
        crawler.unbind()

# 6. RESETTING LOGGING CONFIGURATION
print("\n==== RESETTING LOGGING CONFIGURATION ====")
print("Resetting logging to default settings...")

# Reset to default config
default_config = {
    "logger": {
        "level": logging.INFO,
        "console_enabled": True,
        "file_enabled": False,
        "file_path": None,
        "use_colors": True,
        "component_levels": {},
    }
}
config.update(default_config)

# Apply changes by resetting the logger system
Logger.reset()
print("Logging system reset to defaults")

# Show final log file status and clean up
if os.path.exists(log_file):
    file_size = os.path.getsize(log_file)
    print(f"\nLog file created: {log_file} ({file_size} bytes)")

    # Display the first few lines of the log file
    print("\nLog file preview (first 5 lines):")
    with open(log_file, "r") as f:
        for i, line in enumerate(f):
            if i >= 5:
                break
            print(f"  {line.strip()}")

    # Clean up the log file
    print("\nCleaning up log file...")
    os.remove(log_file)
    print(f"Removed temporary log file: {log_file}")

print("\nExample complete!")
