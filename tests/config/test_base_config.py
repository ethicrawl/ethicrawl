from ethicrawl.config import BaseConfig


class TestBaseConfig(BaseConfig):

    def test_abc_base_config(self):
        self.to_dict()
        repr(self)
        str(self)

    def to_dict(self):
        return super().to_dict()
