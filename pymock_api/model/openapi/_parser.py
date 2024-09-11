from abc import ABCMeta, abstractmethod
from typing import List, Type, cast

from ._base import BaseOpenAPIDataModel, ensure_get_schema_parser_factory
from ._base_schema_parser import BaseSchemaParser
from ._parser_factory import BaseOpenAPISchemaParserFactory
from ._schema_parser import BaseOpenAPISchemaParser


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


class OpenAPIDocumentConfigParser(BaseParser):
    @property
    def parser(self) -> BaseOpenAPISchemaParser:
        return cast(BaseOpenAPISchemaParser, super().parser)

    def process_tags(self, data_modal: Type[BaseOpenAPIDataModel]) -> List[BaseOpenAPIDataModel]:
        return list(map(lambda t: data_modal.generate(t), self.parser.get_tags()))
