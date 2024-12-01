from abc import ABCMeta, abstractmethod
from typing import Dict, Union

from ..enums import OpenAPIVersion
from ._schema_parser import (
    BaseOpenAPIPathSchemaParser,
    BaseOpenAPIResponseSchemaParser,
    BaseOpenAPISchemaParser,
    BaseOpenAPITagSchemaParser,
    OpenAPIResponseSchemaParser,
    OpenAPITagSchemaParser,
    OpenAPIV2PathSchemaParser,
    OpenAPIV2SchemaParser,
    OpenAPIV3PathSchemaParser,
    OpenAPIV3SchemaParser,
)


class BaseOpenAPISchemaParserFactory(metaclass=ABCMeta):
    @abstractmethod
    def chk_version(self, version: OpenAPIVersion) -> bool:
        pass

    @abstractmethod
    def entire_config(self, file: str = "", data: Dict = {}) -> BaseOpenAPISchemaParser:
        pass

    def tag(self, data: Dict) -> BaseOpenAPITagSchemaParser:
        raise NotImplementedError

    @abstractmethod
    def path(self, data: Dict) -> BaseOpenAPIPathSchemaParser:
        pass

    @abstractmethod
    def response(self, data: Dict) -> BaseOpenAPIResponseSchemaParser:
        pass


class OpenAPIV2SchemaParserFactory(BaseOpenAPISchemaParserFactory):
    def chk_version(self, version: OpenAPIVersion) -> bool:
        return version is OpenAPIVersion.V2

    def entire_config(self, file: str = "", data: Dict = {}) -> OpenAPIV2SchemaParser:
        return OpenAPIV2SchemaParser(file=file, data=data)

    def tag(self, data: Dict) -> OpenAPITagSchemaParser:
        return OpenAPITagSchemaParser(data=data)

    def path(self, data: Dict) -> OpenAPIV2PathSchemaParser:
        return OpenAPIV2PathSchemaParser(data=data)

    def response(self, data: Dict) -> OpenAPIResponseSchemaParser:
        return OpenAPIResponseSchemaParser(data=data)


class OpenAPIV3SchemaParserFactory(BaseOpenAPISchemaParserFactory):
    def chk_version(self, version: OpenAPIVersion) -> bool:
        return version is OpenAPIVersion.V3

    def entire_config(self, file: str = "", data: Dict = {}) -> OpenAPIV3SchemaParser:
        return OpenAPIV3SchemaParser(file=file, data=data)

    def path(self, data: Dict) -> OpenAPIV3PathSchemaParser:
        return OpenAPIV3PathSchemaParser(data=data)

    def response(self, data: Dict) -> OpenAPIResponseSchemaParser:
        return OpenAPIResponseSchemaParser(data=data)


def get_schema_parser_factory(version: Union[str, OpenAPIVersion]) -> BaseOpenAPISchemaParserFactory:
    if isinstance(version, str):
        version = OpenAPIVersion.to_enum(version)

    if version is OpenAPIVersion.V2:
        return OpenAPIV2SchemaParserFactory()
    if version is OpenAPIVersion.V3:
        return OpenAPIV3SchemaParserFactory()

    invalid_version = version if isinstance(version, str) else version.name
    raise NotImplementedError(f"PyMock-API doesn't support OpenAPI version {invalid_version}.")
