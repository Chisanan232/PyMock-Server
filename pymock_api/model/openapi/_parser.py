from abc import ABCMeta, abstractmethod
from typing import List, Optional, Type, Union, cast

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
    RequestParameter,
    ResponseProperty,
    TmpHttpConfigV2,
    TmpHttpConfigV3,
    TmpReferenceConfigPropertyModel,
    TmpRequestParameterModel,
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

    def process_api_parameters(self, http_method: str) -> List[RequestParameter]:

        def _deserialize_as_tmp_model(_data: TmpRequestParameterModel) -> RequestParameter:
            return RequestParameter(
                name=_data.name,
                required=(_data.required or False),
                value_type=_data.value_type,
                default=_data.default,
                items=_data.items,  # type: ignore[arg-type]
            )

        def _initial_request_parameters_model(
            _data: List[TmpRequestParameterModel], not_ref_data: List[TmpRequestParameterModel]
        ) -> List[RequestParameter]:
            has_ref_in_schema_param = list(filter(lambda p: p.has_ref() != "", _data))
            if has_ref_in_schema_param:
                # TODO: Ensure the value maps this condition is really only one
                handled_parameters = []
                for d in _data:
                    handled_parameters.extend(self._process_has_ref_parameters(d))
            else:
                # TODO: Parsing the data type of key *items* should be valid type of Python realm
                handled_parameters = [_deserialize_as_tmp_model(p) for p in not_ref_data]
            return handled_parameters

        if get_openapi_version() is OpenAPIVersion.V2:
            v2_params_data: List[dict] = self.parser.get_request_parameters()
            v2_params_data_model = list(map(lambda e: TmpRequestParameterModel().deserialize(e), v2_params_data))
            return _initial_request_parameters_model(v2_params_data_model, v2_params_data_model)
        else:
            if http_method.upper() == "GET":
                get_method_params_data: List[dict] = self.parser.get_request_parameters()
                get_method_params_data_model = list(
                    map(lambda e: TmpRequestParameterModel().deserialize(e), get_method_params_data)
                )
                return _initial_request_parameters_model(get_method_params_data_model, get_method_params_data_model)
            else:
                params_in_path_data: List[dict] = self.parser.get_request_parameters()
                params_data: dict = self.parser.get_request_body()
                params_in_path_data_model = list(
                    map(lambda e: TmpRequestParameterModel().deserialize(e), params_in_path_data)
                )
                params_data_model = TmpRequestParameterModel().deserialize(params_data)
                return _initial_request_parameters_model([params_data_model], params_in_path_data_model)

    def _process_has_ref_parameters(
        self, data: Union[TmpRequestParameterModel, TmpReferenceConfigPropertyModel]
    ) -> List[RequestParameter]:
        request_body_params = data.get_schema_ref()
        # TODO: Should use the reference to get the details of parameters.
        parameters: List[RequestParameter] = []
        for param_name, param_props in request_body_params.properties.items():
            items: Optional[TmpReferenceConfigPropertyModel] = param_props.items
            items_props = []
            if items:
                if items.has_ref():
                    # Sample data:
                    # {
                    #     'type': 'object',
                    #     'required': ['values', 'id'],
                    #     'properties': {
                    #         'values': {'type': 'number', 'example': 23434, 'description': 'value'},
                    #         'id': {'type': 'integer', 'format': 'int64', 'example': 1, 'description': 'ID'}
                    #     },
                    #     'title': 'UpdateOneFooDto'
                    # }
                    item = self._process_has_ref_parameters(data=items)
                    items_props.extend(item)
                else:
                    assert items.value_type
                    items_props.append(
                        RequestParameter.deserialize_by_prps(
                            name="",
                            required=True,
                            value_type=items.value_type,
                            default=items.default,
                            items=[],
                        ),
                    )

            parameters.append(
                RequestParameter.deserialize_by_prps(
                    name=param_name,
                    required=param_name in (request_body_params.required or []),
                    value_type=param_props.value_type or "",
                    default=param_props.default,
                    items=items_props if items is not None else items,  # type: ignore[arg-type]
                ),
            )
        print(f"[DEBUG in APIParser._process_has_ref_parameters] parameters: {parameters}")
        return parameters

    def process_responses(self) -> ResponseProperty:
        # TODO: It may need to add one more data object about outside reference
        # TODO: Replace all *dict* type as tmp object *TmpResponseModel*
        assert self.parser.exist_in_response(status_code="200") is True
        status_200_response = self.parser.get_response(status_code="200")
        print(f"[DEBUG] status_200_response: {status_200_response}")
        tmp_resp_config = TmpHttpConfigV2.deserialize(status_200_response)
        print(f"[DEBUG] tmp_resp_config: {tmp_resp_config}")
        if not tmp_resp_config.is_empty():
            # NOTE: This parsing way for Swagger API (OpenAPI version 2)
            response_data = tmp_resp_config.process_response_from_reference()
        else:
            # FIXME: New implementation to parse configuration will let v2 OpenAPI config come here
            if get_openapi_version() is OpenAPIVersion.V2:
                # response_schema = status_200_response.get("schema", {})
                tmp_resp_config = TmpHttpConfigV2.deserialize(status_200_response)
                has_ref = not tmp_resp_config.is_empty()
            else:
                # NOTE: This parsing way for OpenAPI (OpenAPI version 3)
                status_200_response_model = TmpHttpConfigV3.deserialize(status_200_response)
                # resp_parser = self.schema_parser_factory.response(status_200_response)
                resp_value_format: List[ContentType] = list(
                    filter(
                        lambda ct: status_200_response_model.exist_setting(content_type=ct) is not None,
                        ContentType,
                    )
                )
                print(f"[DEBUG] has content, resp_value_format: {resp_value_format}")
                # response_schema = resp_parser.get_content(value_format=resp_value_format[0])
                tmp_resp_config = status_200_response_model.get_setting(content_type=resp_value_format[0])
                # print(f"[DEBUG] has content, response_schema: {response_schema}")
                # tmp_resp_config = TmpReferenceConfigPropertyModel.deserialize(response_schema)  # type: ignore[assignment]
                has_ref = True if tmp_resp_config.has_ref() else False
            print(f"[DEBUG] has content, tmp_resp_config: {tmp_resp_config}")
            # print(f"[DEBUG] response_schema: {response_schema}")
            if has_ref:
                response_data = tmp_resp_config.process_response_from_reference()
            else:
                # Data may '{}' or '{ "type": "integer", "title": "Id" }'
                tmp_resp_model = TmpReferenceConfigPropertyModel.deserialize({})
                response_data = tmp_resp_model.process_response_from_data()
                # print(f"[DEBUG] response_data: {response_data}")
                # response_data = ResponseProperty.initial_response_data()
                # assert False, "It cannot parse non-reference data."
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
