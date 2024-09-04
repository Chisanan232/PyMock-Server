from abc import ABCMeta, abstractmethod
from typing import List, Type, cast

from ..enums import OpenAPIVersion
from ._base import (
    BaseOpenAPIDataModel,
    ensure_get_schema_parser_factory,
    get_openapi_version,
)
from ._base_schema_parser import BaseSchemaParser
from ._parser_factory import BaseOpenAPISchemaParserFactory
from ._schema_parser import BaseOpenAPIPathSchemaParser, BaseOpenAPISchemaParser
from ._tmp_data_model import (
    ResponseProperty,
    TmpHttpConfigV2,
    TmpHttpConfigV3,
    TmpReferenceConfigPropertyModel,
)
from .content_type import ContentType


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

    def process_responses(self) -> ResponseProperty:
        assert self.parser.exist_in_response(status_code="200") is True
        status_200_response = self.parser.get_response(status_code="200")
        print(f"[DEBUG] status_200_response: {status_200_response}")
        if get_openapi_version() is OpenAPIVersion.V2:
            tmp_resp_config = TmpHttpConfigV2.deserialize(status_200_response)
        else:
            # NOTE: This parsing way for OpenAPI (OpenAPI version 3)
            status_200_response_model = TmpHttpConfigV3.deserialize(status_200_response)
            resp_value_format: List[ContentType] = list(
                filter(lambda ct: status_200_response_model.exist_setting(content_type=ct) is not None, ContentType)
            )
            print(f"[DEBUG] has content, resp_value_format: {resp_value_format}")
            tmp_resp_config = status_200_response_model.get_setting(content_type=resp_value_format[0])

        print(f"[DEBUG] has content, tmp_resp_config: {tmp_resp_config}")
        if tmp_resp_config.has_ref():
            response_data = tmp_resp_config.process_response_from_reference()
        else:
            # Data may '{}' or '{ "type": "integer", "title": "Id" }'
            tmp_resp_model = TmpReferenceConfigPropertyModel.deserialize({})
            response_data = tmp_resp_model.process_response_from_data()
        return response_data

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
