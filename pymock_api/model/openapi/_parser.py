from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Optional, Type, Union, cast

from ..enums import OpenAPIVersion, ResponseStrategy
from ._base import (
    BaseOpenAPIDataModel,
    ensure_get_schema_parser_factory,
    get_openapi_version,
)
from ._base_schema_parser import BaseSchemaParser
from ._js_handlers import ensure_type_is_python_type
from ._parser_factory import BaseOpenAPISchemaParserFactory
from ._schema_parser import (
    BaseOpenAPIPathSchemaParser,
    BaseOpenAPIRequestParametersSchemaParser,
    BaseOpenAPISchemaParser,
    _ReferenceObjectParser,
)
from ._tmp_data_model import (
    ResponseProperty,
    TmpAPIParameterModel,
    TmpRequestItemModel,
    TmpResponsePropertyModel,
    TmpResponseSchema,
)


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


class APIParameterParser(BaseParser):
    @property
    def parser(self) -> BaseOpenAPIRequestParametersSchemaParser:
        return cast(BaseOpenAPIRequestParametersSchemaParser, super().parser)

    def process_parameter(self, data: Dict, accept_no_schema: bool = True) -> TmpAPIParameterModel:
        if not _ReferenceObjectParser.has_schema(data):
            if accept_no_schema:
                return self._convert_from_data(data)
            raise ValueError(f"This data '{data}' doesn't have key 'schema'.")

        if _ReferenceObjectParser.has_ref(data):
            raise NotImplementedError
        else:
            return self._convert_from_parser()

    def _convert_from_data(self, data: dict) -> TmpAPIParameterModel:
        return TmpAPIParameterModel(
            name=data["name"],
            required=data["required"],
            value_type=ensure_type_is_python_type(data["type"]),
            default=data.get("default", None),
            items=[
                TmpRequestItemModel.deserialize(i)
                for i in (self._ensure_data_type_is_pythonic_type_in_items(data.get("items", None)) or [])
            ],
        )

    def _convert_from_parser(self) -> TmpAPIParameterModel:
        return TmpAPIParameterModel(
            name=self.parser.get_name(),
            required=(self.parser.get_required() or False),  # type: ignore[arg-type]
            value_type=ensure_type_is_python_type(self.parser.get_type()),
            default=self.parser.get_default(),
            items=[
                TmpRequestItemModel().deserialize(i)
                for i in (self._ensure_data_type_is_pythonic_type_in_items(self.parser.get_items()) or [])
            ],
        )

    def _ensure_data_type_is_pythonic_type_in_items(
        self, params: Optional[Union[List[dict], Dict[str, Any]]]
    ) -> Optional[List[dict]]:
        new_params = params
        if params:
            # # NOTE: It may get 2 types data:
            # 1.list type:
            # [
            #     {
            #         "name": "value",
            #         "required": true,
            #         "type": "number",
            #         "default": "None"
            #     },
            #     {
            #         "name": "id",
            #         "required": true,
            #         "type": "integer",
            #         "default": "None"
            #     }
            # ]
            # 2. dict type:
            # {
            #     "type": "string",
            #     "enum": [
            #         "ENUM1",
            #         "ENUM2"
            #     ]
            # }
            params = params if isinstance(params, list) else [params]
            new_params: List[dict] = []  # type: ignore[no-redef]
            for param in params:
                assert isinstance(param, dict)
                parser = self.schema_parser_factory.request_parameter_items(param)
                item_data_type = parser.get_items_type()
                if item_data_type:
                    parser.set_items_type(ensure_type_is_python_type(item_data_type))
                param = parser.current_data
                new_params.append(param)  # type: ignore[union-attr]
        return new_params  # type: ignore[return-value]


class APIParser(BaseParser):

    Response_Content_Type: List[str] = ["application/json", "application/octet-stream", "*/*"]

    @property
    def parser(self) -> BaseOpenAPIPathSchemaParser:
        return cast(BaseOpenAPIPathSchemaParser, super().parser)

    def process_api_parameters(self, http_method: str) -> List[TmpAPIParameterModel]:

        def _deserialize_as_tmp_model(_data: dict) -> TmpAPIParameterModel:
            return APIParameterParser(self.schema_parser_factory.request_parameters(_data)).process_parameter(_data)

        def _initial_request_parameters_model(
            _data: List[dict], not_ref_data: List[dict]
        ) -> List[TmpAPIParameterModel]:
            has_ref_in_schema_param = list(filter(lambda p: _ReferenceObjectParser.has_ref(p) != "", _data))
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
            return _initial_request_parameters_model(v2_params_data, v2_params_data)
        else:
            if http_method.upper() == "GET":
                get_method_params_data: List[dict] = self.parser.get_request_parameters()
                return _initial_request_parameters_model(get_method_params_data, get_method_params_data)
            else:
                params_in_path_data: List[dict] = self.parser.get_request_parameters()
                params_data: dict = self.parser.get_request_body()
                return _initial_request_parameters_model([params_data], params_in_path_data)

    def _process_has_ref_parameters(self, data: Dict) -> List[TmpAPIParameterModel]:
        request_body_params = _ReferenceObjectParser.get_schema_ref(data)
        # TODO: Should use the reference to get the details of parameters.
        parameters: List[TmpAPIParameterModel] = []
        parser = self.schema_parser_factory.object(request_body_params)
        for param_name, param_props in parser.get_properties().items():
            props_parser = self.schema_parser_factory.request_parameters(param_props)
            items: Optional[dict] = props_parser.get_items()
            items_props = []
            if items:
                if _ReferenceObjectParser.has_ref(items):
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
                    props_items_parser = self.schema_parser_factory.request_parameter_items(items)
                    item_type = props_items_parser.get_items_type()
                    assert item_type
                    items_props.append(
                        TmpAPIParameterModel(
                            name="",
                            required=True,
                            # "type": convert_js_type(items["type"]),
                            value_type=item_type,
                            default=items.get("default", None),
                            items=[],
                        ),
                    )

            parameters.append(
                TmpAPIParameterModel(
                    name=param_name,
                    required=param_name in parser.get_required(),
                    value_type=param_props["type"],
                    default=param_props.get("default", None),
                    items=items_props if items is not None else items,  # type: ignore[arg-type]
                ),
            )
        print(f"[DEBUG in APIParser._process_has_ref_parameters] parameters: {parameters}")
        return parameters

    def process_responses(self, strategy: ResponseStrategy) -> ResponseProperty:
        # TODO: It may need to add one more data object about outside reference
        # TODO: Replace all *dict* type as tmp object *TmpResponseModel*
        assert self.parser.exist_in_response(status_code="200") is True
        status_200_response = self.parser.get_response(status_code="200")
        # response_data = strategy.initial_response_data()
        print(f"[DEBUG] status_200_response: {status_200_response}")
        tmp_resp_config = TmpResponseSchema.deserialize(status_200_response)
        print(f"[DEBUG] tmp_resp_config: {tmp_resp_config}")
        if not tmp_resp_config.is_empty():
            # NOTE: This parsing way for Swagger API (OpenAPI version 2)
            response_data = tmp_resp_config.process_response_from_reference(
                # init_response=response_data,
                # data=tmp_resp_config,
                get_schema_parser_factory=ensure_get_schema_parser_factory,
            )
            # response_data = strategy.process_response_from_reference(
            #     init_response=response_data,
            #     data=tmp_resp_config,
            #     get_schema_parser_factory=ensure_get_schema_parser_factory,
            # )
        else:
            # FIXME: New implementation to parse configuration will let v2 OpenAPI config come here
            if get_openapi_version() is OpenAPIVersion.V2:
                response_schema = status_200_response.get("schema", {})
                tmp_resp_config = TmpResponseSchema.deserialize(status_200_response)
                has_ref = not tmp_resp_config.is_empty()
            else:
                # NOTE: This parsing way for OpenAPI (OpenAPI version 3)
                resp_parser = self.schema_parser_factory.response(status_200_response)
                resp_value_format = list(
                    filter(lambda vf: resp_parser.exist_in_content(value_format=vf), self.Response_Content_Type)
                )
                print(f"[DEBUG] has content, resp_value_format: {resp_value_format}")
                response_schema = resp_parser.get_content(value_format=resp_value_format[0])
                print(f"[DEBUG] has content, response_schema: {response_schema}")
                tmp_resp_config = TmpResponsePropertyModel.deserialize(response_schema)  # type: ignore[assignment]
                has_ref = True if tmp_resp_config.has_ref() else False
            print(f"[DEBUG] has content, tmp_resp_config: {tmp_resp_config}")
            print(f"[DEBUG] response_schema: {response_schema}")
            if has_ref:
                response_data = tmp_resp_config.process_response_from_reference(
                    # init_response=response_data,
                    # data=tmp_resp_config,
                    get_schema_parser_factory=ensure_get_schema_parser_factory,
                )
                # response_data = strategy.process_response_from_reference(
                #     init_response=response_data,
                #     data=tmp_resp_config,
                #     get_schema_parser_factory=ensure_get_schema_parser_factory,
                # )
            else:
                # Data may '{}' or '{ "type": "integer", "title": "Id" }'
                tmp_resp_model = TmpResponsePropertyModel.deserialize(response_schema)
                response_data = tmp_resp_model.process_response_from_data(
                    # init_response=response_data,
                    # data=tmp_resp_model,
                    get_schema_parser_factory=ensure_get_schema_parser_factory,
                )
                # response_data = strategy.process_response_from_data(
                #     init_response=response_data,
                #     data=tmp_resp_model,
                #     get_schema_parser_factory=ensure_get_schema_parser_factory,
                # )
                print(f"[DEBUG] response_data: {response_data}")
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
