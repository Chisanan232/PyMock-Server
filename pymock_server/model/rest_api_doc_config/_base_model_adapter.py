from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Optional, Union

from pymock_server.model import APIParameter as PyMockRequestProperty
from pymock_server.model.api_config import ResponseProperty as PyMockResponseProperty
from pymock_server.model.api_config.format import Format as PyMockFormat

from ._base import Transferable
from ._js_handlers import ApiDocValueFormat


@dataclass
class BaseFormatModelAdapter:
    formatter: Optional[ApiDocValueFormat] = None
    enum: Optional[List[str]] = None

    @abstractmethod
    def to_pymock_api_config(self) -> Optional[PyMockFormat]:
        pass


# The tmp data model for final result to convert as PyMock-Server
@dataclass
class BasePropertyDetailAdapter(metaclass=ABCMeta):
    name: str = field(default_factory=str)
    required: bool = False
    value_type: Optional[str] = None
    format: Optional[dict] = None
    items: Optional[List["BasePropertyDetailAdapter"]] = None

    def serialize(self) -> dict:
        data = {
            "name": self.name,
            "required": self.required,
            "type": self.value_type,
            "format": self.format,
            "items": [item.serialize() for item in self.items] if self.items else None,
        }
        return self._clear_empty_values(data)

    def _clear_empty_values(self, data):
        new_data = {}
        for k, v in data.items():
            if v is not None:
                new_data[k] = v
        return new_data

    @abstractmethod
    def to_pymock_api_config(self) -> Union[PyMockRequestProperty, PyMockResponseProperty]:
        pass


# The data models for final result which would be converted as the data models of PyMock-Server configuration
@dataclass
class BaseRequestParameterAdapter(BasePropertyDetailAdapter, ABC):
    items: Optional[List["BaseRequestParameterAdapter"]] = None  # type: ignore[assignment]
    default: Optional[Any] = None

    @classmethod
    @abstractmethod
    def deserialize_by_prps(
        cls, name: str = "", required: bool = True, value_type: str = "", default: Any = None, items: List = []
    ) -> "BaseRequestParameterAdapter":
        pass


# The base data model for request and response
@dataclass
class BaseRefPropertyDetailAdapter(BasePropertyDetailAdapter, ABC):
    items: Optional[List["BaseRefPropertyDetailAdapter"]] = None  # type: ignore[assignment]
    is_empty: Optional[bool] = None

    @staticmethod
    @abstractmethod
    def generate_empty_response() -> "BaseRefPropertyDetailAdapter":
        pass


# Just for temporarily use in data process
@dataclass
class BaseResponsePropertyAdapter(metaclass=ABCMeta):
    data: List[BaseRefPropertyDetailAdapter] = field(default_factory=list)

    @staticmethod
    @abstractmethod
    def initial_response_data() -> "BaseRefPropertyDetailAdapter":
        pass


# The tmp data model for final result to convert as PyMock-Server
@dataclass
class BaseAPIAdapter(Transferable, ABC):
    path: str = field(default_factory=str)
    http_method: str = field(default_factory=str)
    parameters: List[BaseRequestParameterAdapter] = field(default_factory=list)
    response: Optional[BaseResponsePropertyAdapter] = None
    tags: Optional[List[str]] = None
