import pytest
import threading
import json
from ethicrawl.config.config import Config, SingletonMeta
from ethicrawl.config.http_config import HttpConfig
from ethicrawl.config.logger_config import LoggerConfig
from ethicrawl.config.sitemap_config import SitemapConfig


class TestSingletonMeta:
    def test_singleton_behavior(self):
        """Test that SingletonMeta enforces the singleton pattern."""

        # Create a test class using SingletonMeta
        class TestSingleton(metaclass=SingletonMeta):
            def __init__(self):
                self.value = 1

        # Get two instances
        instance1 = TestSingleton()
        instance2 = TestSingleton()

        # They should be the same object
        assert instance1 is instance2

        # Changing one should affect the other
        instance1.value = 2
        assert instance2.value == 2

    def test_thread_safety(self):
        """Test that SingletonMeta is thread-safe."""
        # Reset singleton instances to ensure clean test
        SingletonMeta._instances = {}

        # Create a test class using SingletonMeta
        class TestSingleton(metaclass=SingletonMeta):
            def __init__(self):
                self.value = 1

        # Track instances created in threads
        instances = []

        def create_instance():
            instances.append(TestSingleton())

        # Create multiple threads that all try to create an instance
        threads = [threading.Thread(target=create_instance) for _ in range(10)]

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        # All instances should be the same object
        first_instance = instances[0]
        for instance in instances[1:]:
            assert instance is first_instance


class TestConfig:
    @classmethod
    def setup_class(cls):
        """Setup before all tests."""
        # Reset singleton to start with a clean instance
        Config.reset()

    def test_singleton_behavior(self):
        """Test that Config uses the singleton pattern."""
        # Get two instances
        config1 = Config()
        config2 = Config()

        # They should be the same object
        assert config1 is config2

        # Modify one
        config1.http.timeout = 60

        # The other should reflect the change
        assert config2.http.timeout == 60

    def test_initialization(self):
        """Test initial configuration values."""
        # Reset to get a fresh instance with defaults
        Config.reset()
        config = Config()

        # Verify defaults for each section
        assert isinstance(config.http, HttpConfig)
        assert isinstance(config.logger, LoggerConfig)
        assert isinstance(config.sitemap, SitemapConfig)

        # Check specific defaults
        assert config.http.timeout == 30.0
        assert config.logger.level == 20  # INFO level

    def test_get_snapshot(self):
        """Test getting a configuration snapshot."""
        # Setup
        Config.reset()
        config = Config()
        config.http.timeout = 60

        # Get snapshot
        snapshot = config.get_snapshot()

        # Snapshot should have the current values
        assert snapshot.http.timeout == 60

        # Snapshot should be a different object
        assert snapshot is not config

        # Changes to original should not affect snapshot
        config.http.timeout = 30
        assert config.http.timeout == 30
        assert snapshot.http.timeout == 60

    def test_update_method(self):
        """Test updating configuration from dictionary."""
        # Setup
        Config.reset()
        config = Config()

        # Update with dictionary
        config.update(
            {
                "http": {"timeout": 120, "rate_limit": 2.0},
                "logger": {
                    "level": "DEBUG",
                    "component_levels": {"http": "WARNING", "sitemap": "DEBUG"},
                },
            }
        )

        # Verify updates were applied
        assert config.http.timeout == 120
        assert config.http.rate_limit == 2.0
        assert config.logger.level == 10  # DEBUG level
        assert config.logger.component_levels["http"] == 30  # WARNING level
        assert config.logger.component_levels["sitemap"] == 10  # DEBUG level

    def test_update_with_invalid_section(self):
        """Test update with non-existent section."""
        config = Config()

        # This should not raise an exception, just ignore the invalid section
        config.update({"nonexistent_section": {"some_setting": "value"}})

    def test_update_with_invalid_property(self):
        """Test update with non-existent property."""
        config = Config()

        # This should raise an AttributeError
        with pytest.raises(AttributeError):
            config.update({"http": {"nonexistent_property": "value"}})

    def test_reset_class_method(self):
        """Test resetting configuration to defaults."""
        # Setup with non-default values
        config = Config()
        config.http.timeout = 120

        # Reset and get a new instance
        Config.reset()
        new_config = Config()

        # Should have default values
        assert new_config.http.timeout == 30.0

        # Should be a different object
        assert new_config is not config

    def test_to_dict_method(self):
        """Test converting configuration to dictionary."""
        # Setup
        Config.reset()
        config = Config()
        config.http.timeout = 60
        config.logger.level = "DEBUG"

        # Convert to dictionary
        config_dict = config.to_dict()

        # Verify dictionary contents
        assert isinstance(config_dict, dict)
        assert "http" in config_dict
        assert "logger" in config_dict
        assert "sitemap" in config_dict
        assert config_dict["http"]["timeout"] == 60
        assert config_dict["logger"]["level"] == 10  # DEBUG level

    def test_str_representation(self):
        """Test string representation (JSON)."""
        # Setup
        Config.reset()
        config = Config()
        config.http.timeout = 60

        # Get string representation
        config_str = str(config)

        # Should be valid JSON
        config_dict = json.loads(config_str)

        # Verify contents
        assert config_dict["http"]["timeout"] == 60

    def test_thread_safe_access(self):
        """Test thread-safe access to configuration."""
        # Reset to get a clean instance
        Config.reset()

        # Set initial values
        config = Config()
        config.http.timeout = 10

        # Create a list to track values seen by threads
        results = []

        # Function to run in threads
        def modify_and_read():
            # Get the singleton instance
            cfg = Config()

            # Acquire lock to make the sequence of operations atomic
            with cfg._lock:
                # Read value
                old_value = cfg.http.timeout

                # Modify value
                cfg.http.timeout += 10

                # Read new value
                new_value = cfg.http.timeout

            # Record values
            results.append((old_value, new_value))

        # Create and start threads
        threads = [threading.Thread(target=modify_and_read) for _ in range(5)]
        for thread in threads:
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        # Check results
        # Each thread should see an increment of exactly 10 from its perspective
        for old_value, new_value in results:
            assert new_value - old_value == 10

        # Final value should reflect all increments
        assert Config().http.timeout == 10 + (10 * 5)
