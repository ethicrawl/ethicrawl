"""
Configuration System example for Ethicrawl library.

This example demonstrates:
- Accessing and modifying all configuration sections (HTTP, Logger, Sitemap)
- Exporting configuration to JSON and dictionaries
- Importing configuration from external sources
- Understanding thread safety features
"""

import json
import os
import logging
from ethicrawl import Ethicrawl
from ethicrawl.config import Config

# Get the global Config singleton
config = Config()

# 1. EXPLORING DEFAULT CONFIGURATION
print("==== DEFAULT CONFIGURATION VALUES ====")

print("\n--- HTTP Configuration ---")
print(f"User Agent: {config.http.user_agent}")
print(f"Timeout: {config.http.timeout} seconds")
print(f"Max Retries: {config.http.max_retries}")
print(f"Retry Delay: {config.http.retry_delay} seconds")
print(f"Rate Limit: {config.http.rate_limit} requests/second")
print(f"Jitter: {config.http.jitter}")
print(f"Headers: {dict(config.http.headers)}")
print(f"Proxies: {config.http.proxies.to_dict()}")

print("\n--- Logger Configuration ---")
print(f"Log Level: {logging.getLevelName(config.logger.level)}")
print(f"Console Enabled: {config.logger.console_enabled}")
print(f"File Enabled: {config.logger.file_enabled}")
print(f"File Path: {config.logger.file_path}")
print(f"Use Colors: {config.logger.use_colors}")
print(f"Format: {config.logger.format}")
print(f"Component Levels: {config.logger.component_levels}")

print("\n--- Sitemap Configuration ---")
print(f"Max Depth: {config.sitemap.max_depth}")
print(f"Follow External: {config.sitemap.follow_external}")
print(f"Validate URLs: {config.sitemap.validate_urls}")

# 2. MODIFYING CONFIGURATION
print("\n==== MODIFYING CONFIGURATION ====")

# HTTP Configuration
print("\nUpdating HTTP configuration...")
config.http.user_agent = "CustomCrawler/1.0"
config.http.timeout = 45.0
config.http.max_retries = 5
config.http.rate_limit = 0.25  # slower crawling
config.http.headers["Accept-Language"] = "en-US,en;q=0.9"
config.http.proxies.http = "http://localhost:3128"

# Logger Configuration
print("\nUpdating Logger configuration...")
config.logger.level = "DEBUG"
config.logger.file_enabled = True
config.logger.file_path = "ethicrawl_example.log"
config.logger.set_component_level("robots", "DEBUG")
config.logger.set_component_level("http", "WARNING")

# Sitemap Configuration
print("\nUpdating Sitemap configuration...")
config.sitemap.max_depth = 8  # Deeper sitemap recursion
config.sitemap.follow_external = True  # Follow external sitemap links
config.sitemap.validate_urls = True

# 3. EXPORTING CONFIGURATION
print("\n==== EXPORTING CONFIGURATION ====")

# Converting to dictionary
config_dict = config.to_dict()
print("\nExported to dictionary with these sections:")
for section in config_dict:
    print(f"- {section} ({len(config_dict[section])} settings)")

# Convert to JSON string
config_json = str(config)
print(f"\nJSON representation length: {len(config_json)} characters")

# Save to file
config_file = "ethicrawl_config.json"
with open(config_file, "w") as f:
    f.write(config_json)
print(f"\nSaved configuration to {config_file}")

# 4. IMPORTING CONFIGURATION
print("\n==== IMPORTING CONFIGURATION ====")

# Reset some values to defaults first
print("Resetting selected values...")
config.http.user_agent = "Ethicrawl/1.0"
config.logger.level = "INFO"
config.sitemap.max_depth = 5

# Create a configuration dict to import
new_settings = {
    "http": {"user_agent": "ImportedAgent/2.0", "timeout": 60, "rate_limit": 1.0},
    "logger": {"level": "WARNING", "component_levels": {"sitemaps": "DEBUG"}},
    "sitemap": {"max_depth": 10, "follow_external": False},
}

# Update configuration from dict
print("\nImporting new configuration...")
config.update(new_settings)

# Verify updates
print("\nVerified updated values:")
print(f"HTTP User Agent: {config.http.user_agent}")
print(f"HTTP Timeout: {config.http.timeout}")
print(f"Logger Level: {logging.getLevelName(config.logger.level)}")
print(f"Sitemap Max Depth: {config.sitemap.max_depth}")
print(f"Component Levels: {config.logger.component_levels}")

# 5. COMMON USE CASES
print("\n==== COMMON CONFIGURATION USE CASES ====")

print("\n--- Slow, Careful Crawling ---")
print(
    """
# For high-reliability crawling with minimal impact
config = Config()
config.http.rate_limit = 0.1  # Only 1 request per 10 seconds
config.http.jitter = 0.5  # Add 0-50% random variation to delay
config.http.max_retries = 5  # More retries for resilience
config.http.user_agent = "EthicrawlBot/1.0 (https://example.com/bot)"  # Identifiable
config.logger.file_enabled = True  # Log everything for audit trail
"""
)

print("\n--- Deep Sitemap Exploration ---")
print(
    """
# For comprehensive sitemap crawling
config = Config()
config.sitemap.max_depth = 15  # Follow deeply nested sitemaps
config.sitemap.follow_external = True  # Follow external references
config.logger.set_component_level("sitemaps", "DEBUG")  # Detailed sitemap logs
"""
)

print("\n--- Multi-domain Crawling with Different Rates ---")
print(
    """
# Create different clients for different domains
from ethicrawl.client import HttpClient

# Main crawler with global config
ethicrawl = Ethicrawl()
ethicrawl.bind("https://primary-site.com")

# More aggressive crawling for CDN domain
Config().http.rate_limit = 5.0  # 5 requests per second
cdn_client = HttpClient()  # Will use current config
ethicrawl.whitelist("https://cdn.example.com", client=cdn_client)

# Slower crawling for API domain
Config().http.rate_limit = 0.1  # 1 request per 10 seconds
api_client = HttpClient()  # Will use updated config
ethicrawl.whitelist("https://api.example.com", client=api_client)
"""
)

# 6. THREAD SAFETY
print("\n==== THREAD SAFETY FEATURES ====")
print(
    """
Key thread safety features in Ethicrawl's configuration system:

1. All property access is protected by a reentrant lock
2. get_snapshot() provides a consistent read-only view:

   # Get a thread-safe snapshot for reading
   snapshot = Config().get_snapshot()
   # Use values without worrying about changes from other threads
   timeout = snapshot.http.timeout
   retries = snapshot.http.max_retries

3. update() performs atomic configuration changes:

   # Update multiple settings atomically
   Config().update({
       "http": {"timeout": 30, "max_retries": 5},
       "logger": {"level": "DEBUG"}
   })
"""
)

# Clean up
if os.path.exists(config_file):
    os.remove(config_file)
    print(f"\nRemoved temporary config file: {config_file}")

print("\nExample complete!")
