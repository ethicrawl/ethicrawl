import pytest

from ethicrawl.config import Config, ConcurrencyConfig


class TestConcurrencyConfig:
    def test_concurrency_config_exists(self):
        config = Config()
        assert isinstance(config.concurrency, ConcurrencyConfig)
        config.reset()

    def test_concurrency_bounds(self):
        config = Config()

        # check defaults
        assert config.concurrency.enabled == False
        assert config.concurrency.requests == -1
        assert config.concurrency.chrome == -1

        # test enabled
        config.concurrency.enabled = True
        assert config.concurrency.enabled == True
        assert config.concurrency.requests == 1
        assert config.concurrency.chrome == -1

        # disable again
        config.concurrency.enabled = False
        assert config.concurrency.enabled == False
        assert config.concurrency.requests == -1
        assert config.concurrency.chrome == -1

        # set enabled to none boolean
        with pytest.raises(TypeError, match="enabled must be a boolean, got float"):
            config.concurrency.enabled = 0.5

        # set to -2
        with pytest.raises(ValueError, match="requests must be -1 or greater"):
            config.concurrency.requests = -2
        with pytest.raises(ValueError, match="chrome must be -1 or greater"):
            config.concurrency.chrome = -2

        # wrong value
        with pytest.raises(TypeError, match="requests must be an integer, got float"):
            config.concurrency.requests = 0.5
        with pytest.raises(TypeError, match="chrome must be an integer, got float"):
            config.concurrency.chrome = 0.5
