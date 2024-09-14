from abc import ABCMeta, abstractmethod
from typing import Union

from ..enums import OpenAPIVersion


class BaseOpenAPISchemaParserFactory(metaclass=ABCMeta):
    @abstractmethod
    def chk_version(self, version: OpenAPIVersion) -> bool:
        pass


class OpenAPIV2SchemaParserFactory(BaseOpenAPISchemaParserFactory):
    def chk_version(self, version: OpenAPIVersion) -> bool:
        return version is OpenAPIVersion.V2


class OpenAPIV3SchemaParserFactory(BaseOpenAPISchemaParserFactory):
    def chk_version(self, version: OpenAPIVersion) -> bool:
        return version is OpenAPIVersion.V3


def get_schema_parser_factory(version: Union[str, OpenAPIVersion]) -> BaseOpenAPISchemaParserFactory:
    if isinstance(version, str):
        version = OpenAPIVersion.to_enum(version)

    if version is OpenAPIVersion.V2:
        return OpenAPIV2SchemaParserFactory()
    if version is OpenAPIVersion.V3:
        return OpenAPIV3SchemaParserFactory()

    invalid_version = version if isinstance(version, str) else version.name
    raise NotImplementedError(f"PyMock-API doesn't support OpenAPI version {invalid_version}.")
