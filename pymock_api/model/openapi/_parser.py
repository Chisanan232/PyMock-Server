from abc import ABCMeta, abstractmethod
from typing import List, Type, cast

from ._base import BaseOpenAPIDataModel, ensure_get_schema_parser_factory
from ._base_schema_parser import BaseSchemaParser
from ._parser_factory import BaseOpenAPISchemaParserFactory
from ._schema_parser import BaseOpenAPIPathSchemaParser, BaseOpenAPISchemaParser


class BaseParser(metaclass=ABCMeta):
    def __init__(self, parser: BaseSchemaParser):
        self._parser = parser

    @property
    @abstractmethod
    def parser(self) -> BaseSchemaParser:
        return self._parser

    @property
    def schema_parser_factory(self) -> BaseOpenAPISchemaParserFactory:
        return ensure_get_schema_parser_factory()


class APIParser(BaseParser):

    @property
    def parser(self) -> BaseOpenAPIPathSchemaParser:
        return cast(BaseOpenAPIPathSchemaParser, super().parser)

    def process_tags(self) -> List[str]:
        return self.parser.get_all_tags()


class OpenAPIDocumentConfigParser(BaseParser):
    @property
    def parser(self) -> BaseOpenAPISchemaParser:
        return cast(BaseOpenAPISchemaParser, super().parser)

    def process_paths(self, data_modal: Type[BaseOpenAPIDataModel]) -> List[BaseOpenAPIDataModel]:
        apis = self.parser.get_paths()
        paths = []
        for api_path, api_props in apis.items():
            for one_api_http_method, one_api_details in api_props.items():
                paths.append(
                    data_modal.generate(api_path=api_path, http_method=one_api_http_method, detail=one_api_details)
                )
        return paths

    def process_tags(self, data_modal: Type[BaseOpenAPIDataModel]) -> List[BaseOpenAPIDataModel]:
        return list(map(lambda t: data_modal.generate(t), self.parser.get_tags()))
