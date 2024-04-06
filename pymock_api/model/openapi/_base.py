from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Union

from ..api_config import _Config
from ..enums import OpenAPIVersion
from ._parser_factory import BaseOpenAPISchemaParserFactory, get_parser_factory

Self = Any

OpenAPI_Document_Version: OpenAPIVersion = OpenAPIVersion.V3
OpenAPI_Parser_Factory: BaseOpenAPISchemaParserFactory = get_parser_factory(version=OpenAPI_Document_Version)


def get_openapi_version() -> OpenAPIVersion:
    global OpenAPI_Document_Version
    return OpenAPI_Document_Version


def set_openapi_version(v: Union[str, OpenAPIVersion]) -> None:
    global OpenAPI_Document_Version
    OpenAPI_Document_Version = OpenAPIVersion.to_enum(v)


def set_parser_factory(f: BaseOpenAPISchemaParserFactory) -> None:
    global OpenAPI_Parser_Factory
    OpenAPI_Parser_Factory = f


class BaseOpenAPIDataModel(metaclass=ABCMeta):

    @property
    def parser_factory(self) -> BaseOpenAPISchemaParserFactory:
        global OpenAPI_Document_Version, OpenAPI_Parser_Factory
        assert (
            OpenAPI_Parser_Factory.chk_version(OpenAPI_Document_Version) is True
        ), "The parser factory is not mapping with the OpenAPI documentation version."
        return OpenAPI_Parser_Factory

    def load_parser_factory_with_openapi_version(self) -> BaseOpenAPISchemaParserFactory:
        global OpenAPI_Document_Version
        return get_parser_factory(version=OpenAPI_Document_Version)

    def reload_parser_factory(self) -> None:
        self._load_parser_factory()

    def _load_parser_factory(self) -> None:
        set_parser_factory(self.load_parser_factory_with_openapi_version())

    @abstractmethod
    def deserialize(self, data: Dict) -> Self:
        pass


class Transferable(BaseOpenAPIDataModel):
    @abstractmethod
    def to_api_config(self, **kwargs) -> _Config:
        pass
