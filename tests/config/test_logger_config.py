import pytest
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

from ethicrawl.config import LoggerConfig


class TestLoggerConfig:
    def test_level_setter(self):
        lc = LoggerConfig()
        lc.level = 10
        lc_strings = [
            "debug",
            "info",
            "warning",
            "error",
            "critical",
            "Critical",
            "CritiCAL",
            "CRITICAL",
        ]
        for level in lc_strings:
            lc.level = level

        with pytest.raises(
            ValueError,
            match="Invalid log level name: 'foo'. Valid levels are: DEBUG, INFO, WARNING, ERROR, CRITICAL",
        ):
            lc.level = "foo"

        with pytest.raises(ValueError, match="Invalid integer log level: 0"):
            lc.level = 0

        with pytest.raises(
            TypeError, match="Log level must be an integer or level name string"
        ):
            lc.level = 1.0

    def test_console_enabled(self):
        lc = LoggerConfig()
        with pytest.raises(TypeError, match="console_enabled must be a boolean"):
            lc.console_enabled = "foo"

    def test_file_enabled_path(self):
        lc = LoggerConfig()
        with pytest.raises(TypeError, match="file_enabled must be a boolean"):
            lc.file_enabled = "foo"
        lc.file_path = None
        assert lc.file_path == None
        lc.file_path = "foo"
        assert lc.file_path == "foo"
        with pytest.raises(TypeError, match="file_path must be a string or None"):
            lc.file_path = []

    def test_colors_format(self):
        lc = LoggerConfig()
        lc.use_colors = True
        with pytest.raises(TypeError, match="use_colors must be a boolean"):
            lc.use_colors = "foo"
        lc.format = "foo"
        with pytest.raises(ValueError, match="format string cannot be empty"):
            lc.format = ""
        with pytest.raises(TypeError, match="format must be a string"):
            lc.format = 1

    def test_component_levels(self):
        lc = LoggerConfig()
        lc.set_component_level("foo", 10)
