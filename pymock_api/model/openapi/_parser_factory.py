from abc import ABCMeta, abstractmethod
from typing import Dict, Union

from ..enums import OpenAPIVersion
from ._parse import (
    BaseOpenAPIObjectParser,
    BaseOpenAPIParser,
    BaseOpenAPIPathParser,
    BaseOpenAPIRequestParametersParser,
    BaseOpenAPIResponseParser,
    BaseOpenAPITagParser,
    OpenAPIObjectParser,
    OpenAPIParser,
    OpenAPIPathParser,
    OpenAPIRequestParametersParser,
    OpenAPIResponseParser,
    OpenAPITagParser,
    OpenAPIV3Parser,
)


class BaseOpenAPIParserFactory(metaclass=ABCMeta):

    @abstractmethod
    def entire_config(self, file: str = "", data: Dict = {}) -> BaseOpenAPIParser:
        pass

    @abstractmethod
    def tag(self, data: Dict) -> BaseOpenAPITagParser:
        pass

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

    def entire_config(self, file: str = "", data: Dict = {}) -> OpenAPIParser:
        return OpenAPIParser(file=file, data=data)

    def tag(self, data: Dict) -> OpenAPITagParser:
        return OpenAPITagParser(data=data)

    def path(self, data: Dict) -> OpenAPIPathParser:
        return OpenAPIPathParser(data=data)

    def request_parameters(self, data: Dict) -> OpenAPIRequestParametersParser:
        return OpenAPIRequestParametersParser(data=data)

    def response(self, data: Dict) -> OpenAPIResponseParser:
        return OpenAPIResponseParser(data=data)

    def object(self, data: Dict) -> OpenAPIObjectParser:
        return OpenAPIObjectParser(data=data)


class OpenAPIV3ParserFactory(BaseOpenAPIParserFactory):

    def entire_config(self, file: str = "", data: Dict = {}) -> OpenAPIV3Parser:
        return OpenAPIV3Parser(file=file, data=data)

    def tag(self, data: Dict) -> OpenAPITagParser:
        return OpenAPITagParser(data=data)

    def path(self, data: Dict) -> OpenAPIPathParser:
        return OpenAPIPathParser(data=data)

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
