from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from fake_api_server.model.api_config import _Config

from .version import OpenAPIVersion

Self = Any

OpenAPI_Document_Version: OpenAPIVersion = OpenAPIVersion.V3


def get_openapi_version() -> OpenAPIVersion:
    global OpenAPI_Document_Version
    return OpenAPI_Document_Version


def set_openapi_version(v: Union[str, OpenAPIVersion]) -> None:
    global OpenAPI_Document_Version
    OpenAPI_Document_Version = OpenAPIVersion.to_enum(v)


@dataclass
class BaseOpenAPIDataModel(metaclass=ABCMeta):

    @classmethod
    def generate(cls, *args, **kwargs) -> Self:
        raise NotImplementedError

    @abstractmethod
    def deserialize(self, data: Dict) -> Self:
        pass


@dataclass
class Transferable(BaseOpenAPIDataModel):
    @abstractmethod
    def to_api_config(self, **kwargs) -> _Config:
        pass


@dataclass
class BaseProperty(BaseOpenAPIDataModel, ABC):
    name: str = field(default_factory=str)
    required: bool = False
    value_type: str = field(default_factory=str)
    default: Any = None
    items: Optional[List[BaseOpenAPIDataModel]] = None
