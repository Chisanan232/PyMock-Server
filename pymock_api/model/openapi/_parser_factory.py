from abc import ABCMeta, abstractmethod
from typing import Dict

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


class OpenAPIParserFactory(BaseOpenAPIParserFactory):

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
