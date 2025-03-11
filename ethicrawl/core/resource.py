from dataclasses import dataclass
from ethicrawl.core.url import Url


@dataclass
class Resource:
    url: Url

    def __post_init__(self):
        if isinstance(self.url, str):  # user provided a str; cast to Url
            self.url = Url(self.url)
        if not isinstance(self.url, Url):
            raise ValueError(
                f"Error creating resource, got type {type(self.url)} expected str or Url"
            )

    # def __str__(self):
    #     return self.url.__str__
