from abc import ABCMeta, abstractmethod
from typing import Dict, Union

from ..enums import OpenAPIVersion
from ._schema_parser import (
    BaseOpenAPIObjectParser,
    BaseOpenAPIParser,
    BaseOpenAPIPathParser,
    BaseOpenAPIRequestParametersParser,
    BaseOpenAPIResponseParser,
    BaseOpenAPITagParser,
    OpenAPIObjectParser,
    OpenAPIRequestParametersParser,
    OpenAPIResponseParser,
    OpenAPITagParser,
    OpenAPIV2Parser,
    OpenAPIV2PathParser,
    OpenAPIV3Parser,
    OpenAPIV3PathParser,
)


class BaseOpenAPIParserFactory(metaclass=ABCMeta):
    @abstractmethod
    def chk_version(self, version: OpenAPIVersion) -> bool:
        pass

    @abstractmethod
    def entire_config(self, file: str = "", data: Dict = {}) -> BaseOpenAPIParser:
        pass

    def tag(self, data: Dict) -> BaseOpenAPITagParser:
        raise NotImplementedError

    @abstractmethod
    def path(self, data: Dict) -> BaseOpenAPIPathParser:
        pass

    @abstractmethod
    def request_parameters(self, data: Dict) -> BaseOpenAPIRequestParametersParser:
        pass

    @abstractmethod
    def response(self, data: Dict) -> BaseOpenAPIResponseParser:
        pass

    @abstractmethod
    def object(self, data: Dict) -> BaseOpenAPIObjectParser:
        pass


class OpenAPIV2ParserFactory(BaseOpenAPIParserFactory):
    def chk_version(self, version: OpenAPIVersion) -> bool:
        return version is OpenAPIVersion.V2

    def entire_config(self, file: str = "", data: Dict = {}) -> OpenAPIV2Parser:
        return OpenAPIV2Parser(file=file, data=data)

    def tag(self, data: Dict) -> OpenAPITagParser:
        return OpenAPITagParser(data=data)

    def path(self, data: Dict) -> OpenAPIV2PathParser:
        return OpenAPIV2PathParser(data=data)

    def request_parameters(self, data: Dict) -> OpenAPIRequestParametersParser:
        return OpenAPIRequestParametersParser(data=data)

    def response(self, data: Dict) -> OpenAPIResponseParser:
        return OpenAPIResponseParser(data=data)

    def object(self, data: Dict) -> OpenAPIObjectParser:
        return OpenAPIObjectParser(data=data)


class OpenAPIV3ParserFactory(BaseOpenAPIParserFactory):
    def chk_version(self, version: OpenAPIVersion) -> bool:
        return version is OpenAPIVersion.V3

    def entire_config(self, file: str = "", data: Dict = {}) -> OpenAPIV3Parser:
        return OpenAPIV3Parser(file=file, data=data)

    def path(self, data: Dict) -> OpenAPIV3PathParser:
        return OpenAPIV3PathParser(data=data)

    def request_parameters(self, data: Dict) -> OpenAPIRequestParametersParser:
        return OpenAPIRequestParametersParser(data=data)

    def response(self, data: Dict) -> OpenAPIResponseParser:
        return OpenAPIResponseParser(data=data)

    def object(self, data: Dict) -> OpenAPIObjectParser:
        return OpenAPIObjectParser(data=data)


def get_parser_factory(version: Union[str, OpenAPIVersion]) -> BaseOpenAPIParserFactory:
    if isinstance(version, str):
        version = OpenAPIVersion.to_enum(version)

    if version is OpenAPIVersion.V2:
        return OpenAPIV2ParserFactory()
    if version is OpenAPIVersion.V3:
        return OpenAPIV3ParserFactory()

    invalid_version = version if isinstance(version, str) else version.name
    raise NotImplementedError(f"PyMock-API doesn't support OpenAPI version {invalid_version}.")
