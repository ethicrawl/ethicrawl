import pytest
from ethicrawl.config import Config
from ethicrawl.logger import Logger


@pytest.fixture(autouse=True)
def reset_all_singletons():
    """Reset all singleton classes before and after each test."""
    # Reset before test
    Config().reset()
    Logger().reset()

    # Run the test
    yield

    # Reset after test
    Config().reset()
    Logger().reset()
