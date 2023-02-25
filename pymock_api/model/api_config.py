"""*The data objects of configuration*

content ...
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class BaseConfig:
    """*The **base** section in **mocked_apis***"""

    url: str


@dataclass
class HTTPRequest:
    """*The **http.request** section in **mocked_apis.<api>***"""

    method: str
    parameters: dict = field(default_factory=dict)


@dataclass
class HTTPResponse:
    """*The **http.response** section in **mocked_apis.<api>***"""

    value: str


@dataclass
class HTTP:
    """*The **http** section in **mocked_apis.<api>***"""

    request: HTTPRequest
    response: HTTPResponse


@dataclass
class MockAPI:
    """*The **<api>** section in **mocked_apis***"""

    url: str
    http: HTTP


@dataclass
class MockAPIs:
    """*The **mocked_apis** section*"""

    base: BaseConfig
    apis: Dict[str, MockAPI]

    def __len__(self):
        return len(self.apis.keys())


@dataclass
class APIConfig:
    """*The entire configuration*"""

    apis: MockAPIs
    name: str = ""
    description: str = ""

    def __len__(self):
        return len(self.apis) if self.apis else 0

    def has_apis(self) -> bool:
        return len(self) != 0
