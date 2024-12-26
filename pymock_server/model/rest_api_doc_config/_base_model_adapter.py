import logging
from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Optional, Union

from pymock_server.model import APIParameter as PyMockRequestProperty
from pymock_server.model.api_config import ResponseProperty as PyMockResponseProperty
from pymock_server.model.api_config.format import Format as PyMockFormat

from ._base import Transferable
from ._js_handlers import ApiDocValueFormat

logger = logging.getLogger(__name__)


@dataclass
class BaseFormatModelAdapter:
    formatter: Optional[ApiDocValueFormat] = None
    enum: Optional[List[str]] = None

    def is_none(self) -> bool:
        return self.formatter is None and not self.enum

    @abstractmethod
    def to_pymock_api_config(self) -> Optional[PyMockFormat]:
        pass


# The tmp data model for final result to convert as PyMock-Server
@dataclass
class BasePropertyDetailAdapter(metaclass=ABCMeta):
    name: str = field(default_factory=str)
    required: bool = False
    value_type: Optional[str] = None
    format: Optional[BaseFormatModelAdapter] = None
    items: Optional[List["BasePropertyDetailAdapter"]] = None

    def __post_init__(self) -> None:
        if self.items is not None:
            self.items = self._convert_items()

    def _convert_items(self) -> List["BasePropertyDetailAdapter"]:
        items: List["BasePropertyDetailAdapter"] = []
        for item in self.items or []:
            assert isinstance(item, (dict, BasePropertyDetailAdapter))
            if isinstance(item, dict):
                item = self._instantiate_obj(**item)
            items.append(item)
        return items

    @abstractmethod
    def _instantiate_obj(self, **kwargs) -> "BasePropertyDetailAdapter":
        pass

    def serialize(self) -> dict:
        _format = self.format.to_pymock_api_config() if self.format else None
        _format_params = _format.serialize() if _format else None
        data = {
            "name": self.name,
            "required": self.required,
            "type": self.value_type,
            "value_format": _format_params,
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
        cls,
        name: str = "",
        required: bool = True,
        value_type: str = "",
        formatter: Optional[ApiDocValueFormat] = None,
        enum: Optional[List[str]] = None,
        default: Any = None,
        items: List = [],
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
