import pytest
import json

from ethicrawl.config import Config


class TestConfig:

    def test_snapshot(self):
        c1 = Config()
        c2 = Config()
        assert c1 is c2
        c3 = c1.get_snapshot()
        assert c1 is not c3

    def test_update(self):
        assert Config().http.user_agent == "Ethicrawl/1.0"
        Config().http.user_agent = "Ethicrawl/1.0-test"
        assert Config().http.user_agent == "Ethicrawl/1.0-test"
        d = Config().to_dict()
        assert d["http"]["user_agent"] == "Ethicrawl/1.0-test"
        d["http"]["user_agent"] = "Ethicrawl/1.0"
        Config().update(d)
        assert Config().http.user_agent == "Ethicrawl/1.0"

    def test_json(self):
        d = json.loads(str(Config()))
        assert isinstance(d, dict)

    def test_reset(self):
        d1 = Config().to_dict()
        Config().http.user_agent = "test"
        d2 = Config().to_dict()
        assert d1 != d2
        Config.reset()
        d3 = Config().to_dict()
        assert d1 == d3

    def test_update_edge_cases(self):
        d = Config().to_dict()
        d["foo"] = "bar"  # FIXME: silently ignored - maybe raise an error?
        Config().update(d)

        d = Config().to_dict()
        d["logger"]["component_levels"]["foo"] = 10
        Config().update(d)

        d = Config().to_dict()
        with pytest.raises(
            AttributeError, match="No such property: 'foo' on http config"
        ):
            d["http"]["foo"] = "bar"
            Config().update(d)

    def test_weird_edge_cases(self):
        Config().__dict__["foo"] = 1
        Config().__dict__["_foo"] = 1
        Config().__dict__["http"].__dict__["_a"] = 1
        Config().to_dict()
        Config().http.__dict__["public_attr"] = "test value"
        d = Config().to_dict()
        assert "public_attr" in d["http"]
        assert d["http"]["public_attr"] == "test value"
