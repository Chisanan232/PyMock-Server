from abc import ABCMeta, abstractmethod
from collections import namedtuple
from typing import Dict, List, Optional, Type, cast

from ..enums import OpenAPIVersion, ResponseStrategy
from ._base import (
    BaseOpenAPIDataModel,
    _YamlSchema,
    ensure_get_schema_parser_factory,
    get_openapi_version,
)
from ._js_handlers import convert_js_type, ensure_type_is_python_type
from ._parser_factory import BaseOpenAPISchemaParserFactory
from ._schema_parser import (
    BaseOpenAPIPathSchemaParser,
    BaseOpenAPIRequestParametersSchemaParser,
    BaseOpenAPISchemaParser,
    BaseSchemaParser,
)

OpenAPIAPIParameterConfig = namedtuple(  # type: ignore[misc]
    typename="OpenAPIAPIParameterConfig",
    field_names=("name", "required", "type", "default", "items"),
    defaults={"default": None, "items": None},  # type: ignore[misc]
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

    def process_parameter(self, data: Dict, accept_no_schema: bool = True) -> OpenAPIAPIParameterConfig:
        if not _YamlSchema.has_schema(data):
            if accept_no_schema:
                return self._convert_from_data(data)
            raise ValueError(f"This data '{data}' doesn't have key 'schema'.")

        if _YamlSchema.has_ref(data):
            raise NotImplementedError
        else:
            return self._convert_from_parser()

    def _convert_from_data(self, data: dict) -> OpenAPIAPIParameterConfig:
        return OpenAPIAPIParameterConfig(  # type: ignore[call-arg]
            name=data["name"],
            required=data["required"],
            type=data["type"],
            default=data.get("default", None),
            items=data.get("items", None),
        )

    def _convert_from_parser(self) -> OpenAPIAPIParameterConfig:
        return OpenAPIAPIParameterConfig(  # type: ignore[call-arg]
            name=self.parser.get_name(),
            required=self.parser.get_required(),
            type=self.parser.get_type(),
            default=self.parser.get_default(),
            items=self.parser.get_items(),
        )


class APIParser(BaseParser):

    Response_Content_Type: List[str] = ["application/json", "application/octet-stream", "*/*"]

    @property
    def parser(self) -> BaseOpenAPIPathSchemaParser:
        return cast(BaseOpenAPIPathSchemaParser, super().parser)

    def process_api_parameters(
        self, data_modal: Type[BaseOpenAPIDataModel], http_method: str
    ) -> List[BaseOpenAPIDataModel]:

        def _initial_non_ref_parameters_value(_params: List[dict]) -> List[dict]:
            for param in _params:
                parser = self.schema_parser_factory.request_parameters(param)
                items = parser.get_items()
                if items is not None:
                    param["items"]["type"] = ensure_type_is_python_type(param["items"]["type"])
            return _params

        def _initial_request_parameters_model() -> List[BaseOpenAPIDataModel]:
            params_data: List[dict] = self.parser.get_request_parameters()
            print(f"[DEBUG] params_data: {params_data}")
            has_ref_in_schema_param = list(filter(lambda p: _YamlSchema.has_ref(p) != "", params_data))
            print(f"[DEBUG in src] has_ref_in_schema_param: {has_ref_in_schema_param}")
            if has_ref_in_schema_param:
                # TODO: Ensure the value maps this condition is really only one
                handled_parameters = []
                for param in params_data:
                    one_handled_parameters = self._process_has_ref_parameters(param)
                    handled_parameters.extend(one_handled_parameters)
            else:
                # TODO: Parsing the data type of key *items* should be valid type of Python realm
                handled_parameters = _initial_non_ref_parameters_value(params_data)
            return list(map(lambda p: data_modal.generate(detail=p), handled_parameters))

        if get_openapi_version() is OpenAPIVersion.V2:
            return _initial_request_parameters_model()
        else:
            if http_method.upper() == "GET":
                return _initial_request_parameters_model()
            else:
                print(f"[DEBUG in src] get_method_callback(): {http_method}")
                print(f"[DEBUG in src] self.parser._data: {self.parser._data}")
                params_in_path_data: List[dict] = self.parser.get_request_parameters()
                params_data: dict = self.parser.get_request_body()
                print(f"[DEBUG] params_data: {params_data}")
                has_ref_in_schema_param = list(filter(lambda p: _YamlSchema.has_ref(p) != "", [params_data]))
                print(f"[DEBUG in src] has_ref_in_schema_param: {has_ref_in_schema_param}")
                if has_ref_in_schema_param:
                    # TODO: Ensure the value maps this condition is really only one
                    handled_parameters = []
                    one_handled_parameters = self._process_has_ref_parameters(params_data)
                    handled_parameters.extend(one_handled_parameters)
                else:
                    # TODO: Parsing the data type of key *items* should be valid type of Python realm
                    handled_parameters = _initial_non_ref_parameters_value(params_in_path_data)
                return list(map(lambda p: data_modal.generate(detail=p), handled_parameters))

    def _process_has_ref_parameters(self, data: Dict) -> List[dict]:
        request_body_params = _YamlSchema.get_schema_ref(data)
        # TODO: Should use the reference to get the details of parameters.
        parameters: List[dict] = []
        parser = self.schema_parser_factory.object(request_body_params)
        for param_name, param_props in parser.get_properties().items():
            items: Optional[dict] = param_props.get("items", None)
            items_props = []
            if items and _YamlSchema.has_ref(items):
                items = _YamlSchema.get_schema_ref(items)
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
                items_parser = self.schema_parser_factory.object(items)
                for item_name, item_prop in items_parser.get_properties(default={}).items():
                    items_props.append(
                        {
                            "name": item_name,
                            "required": item_name in items_parser.get_required(),
                            "type": convert_js_type(item_prop["type"]),
                            "default": item_prop.get("default", None),
                        }
                    )

            parameters.append(
                {
                    "name": param_name,
                    "required": param_name in parser.get_required(),
                    "type": param_props["type"],
                    "default": param_props.get("default", None),
                    "items": items_props if items is not None else items,
                }
            )
        return parameters

    def process_responses(self, strategy: ResponseStrategy) -> dict:

        # def _initial_response_model_with_ref_value(resp_data: Dict[str, Any], _data: dict) -> Dict[str, Any]:
        #     response_schema_ref = _YamlSchema.get_schema_ref(_data)
        #     parser = self.schema_parser_factory.object(response_schema_ref)
        #     response_schema_properties: Optional[dict] = parser.get_properties(default=None)
        #     if response_schema_properties:
        #         for k, v in response_schema_properties.items():
        #             if strategy is ResponseStrategy.OBJECT:
        #                 # response_data_prop = self._process_response_value(property_value=v, strategy=strategy)
        #                 response_data_prop = strategy.generate_response(
        #                     property_value=v,
        #                     get_schema_parser_factory=ensure_get_schema_parser_factory,
        #                     has_ref_callback=_YamlSchema.has_ref,
        #                     get_ref_callback=_YamlSchema.get_schema_ref,
        #                 )
        #                 assert isinstance(response_data_prop, dict)
        #                 response_data_prop["name"] = k
        #                 response_data_prop["required"] = k in parser.get_required(default=[k])
        #                 assert isinstance(
        #                     resp_data["data"], list
        #                 ), "The response data type must be *list* if its HTTP response strategy is object."
        #                 resp_data["data"].append(response_data_prop)
        #             else:
        #                 assert isinstance(
        #                     resp_data["data"], dict
        #                 ), "The response data type must be *dict* if its HTTP response strategy is not object."
        #                 # resp_data["data"][k] = self._process_response_value(property_value=v, strategy=strategy)
        #                 resp_data["data"][k] = strategy.generate_response(
        #                     property_value=v,
        #                     get_schema_parser_factory=ensure_get_schema_parser_factory,
        #                     has_ref_callback=_YamlSchema.has_ref,
        #                     get_ref_callback=_YamlSchema.get_schema_ref,
        #                 )
        #     return resp_data

        # def _initial_response_model_with_no_ref_value(resp_data: Dict[str, Any], _data: dict) -> Dict[str, Any]:
        #     if strategy is ResponseStrategy.OBJECT:
        #         # response_data_prop = self._process_response_value(property_value=_data, strategy=strategy)
        #         response_data_prop = strategy.generate_response(
        #             property_value=_data,
        #             get_schema_parser_factory=ensure_get_schema_parser_factory,
        #             has_ref_callback=_YamlSchema.has_ref,
        #             get_ref_callback=_YamlSchema.get_schema_ref,
        #         )
        #         assert isinstance(response_data_prop, dict)
        #         assert isinstance(
        #             resp_data["data"], list
        #         ), "The response data type must be *list* if its HTTP response strategy is object."
        #         resp_data["data"].append(response_data_prop)
        #     else:
        #         assert isinstance(
        #             resp_data["data"], dict
        #         ), "The response data type must be *dict* if its HTTP response strategy is not object."
        #         # resp_data["data"][0] = self._process_response_value(property_value=_data, strategy=strategy)
        #         resp_data["data"][0] = strategy.generate_response(
        #             property_value=_data,
        #             get_schema_parser_factory=ensure_get_schema_parser_factory,
        #             has_ref_callback=_YamlSchema.has_ref,
        #             get_ref_callback=_YamlSchema.get_schema_ref,
        #         )
        #     return resp_data

        assert self.parser.exist_in_response(status_code="200") is True
        status_200_response = self.parser.get_response(status_code="200")
        response_data = strategy.initial_response_data()
        # if strategy is ResponseStrategy.OBJECT:
        #     response_data = {
        #         "strategy": strategy,
        #         "data": [],
        #     }
        # else:
        #     response_data = {
        #         "strategy": strategy,
        #         "data": {},
        #     }
        print(f"[DEBUG] status_200_response: {status_200_response}")
        if _YamlSchema.has_schema(status_200_response):
            # response_data = _initial_response_model_with_ref_value(response_data, status_200_response)
            response_data = strategy.process_response_from_reference(
                init_response=response_data,
                data=status_200_response,
                get_schema_parser_factory=ensure_get_schema_parser_factory,
                has_ref_callback=_YamlSchema.has_ref,
                get_ref_callback=_YamlSchema.get_schema_ref,
            )
            # response_data = strategy.process_response_from_reference(
            #     init_resp_data=response_data,
            #     data=status_200_response,
            #     get_schema_parser_factory=ensure_get_schema_parser_factory,
            #     has_ref_callback=_YamlSchema.has_ref,
            #     get_ref_callback=_YamlSchema.get_schema_ref,
            # )
        else:
            resp_parser = self.schema_parser_factory.response(status_200_response)
            resp_value_format = list(
                filter(lambda vf: resp_parser.exist_in_content(value_format=vf), self.Response_Content_Type)
            )
            response_schema = resp_parser.get_content(value_format=resp_value_format[0])
            if _YamlSchema.has_ref(response_schema):
                # response_data = _initial_response_model_with_ref_value(response_data, response_schema)
                response_data = strategy.process_response_from_reference(
                    init_response=response_data,
                    data=response_schema,
                    get_schema_parser_factory=ensure_get_schema_parser_factory,
                    has_ref_callback=_YamlSchema.has_ref,
                    get_ref_callback=_YamlSchema.get_schema_ref,
                )
                # response_data = strategy.process_response_from_reference(
                #     init_resp_data=response_data,
                #     data=status_200_response,
                #     get_schema_parser_factory=ensure_get_schema_parser_factory,
                #     has_ref_callback=_YamlSchema.has_ref,
                #     get_ref_callback=_YamlSchema.get_schema_ref,
                # )
            else:
                print(f"[DEBUG] response_schema: {response_schema}")
                # Data may '{}' or '{ "type": "integer", "title": "Id" }'
                # response_data = _initial_response_model_with_no_ref_value(response_data, response_schema)
                response_data = strategy.process_response_from_data(
                    init_response=response_data,
                    data=response_schema,
                    get_schema_parser_factory=ensure_get_schema_parser_factory,
                    has_ref_callback=_YamlSchema.has_ref,
                    get_ref_callback=_YamlSchema.get_schema_ref,
                )
                # response_data = strategy.process_response_from_data(
                #     init_resp_data=response_data,
                #     data=status_200_response,
                #     get_schema_parser_factory=ensure_get_schema_parser_factory,
                #     has_ref_callback=_YamlSchema.has_ref,
                #     get_ref_callback=_YamlSchema.get_schema_ref,
                # )
                print(f"[DEBUG] response_data: {response_data}")
        return response_data

    # def _process_response_value(self, property_value: dict, strategy: ResponseStrategy) -> Union[str, list, dict]:
    #
    #     # def _handle_empty_data() -> Union[str, dict]:
    #     #     # FIXME: use new function *generate_empty_response*
    #     #     if strategy is ResponseStrategy.OBJECT:
    #     #         return {
    #     #             "name": "",
    #     #             # TODO: Set the *required* property correctly
    #     #             "required": False,
    #     #             # TODO: Set the *type* property correctly
    #     #             "type": None,
    #     #             # TODO: Set the *format* property correctly
    #     #             "format": None,
    #     #             "items": [],
    #     #         }
    #     #     else:
    #     #         return "empty value"
    #     #
    #     # def _handle_ref_data(resp_prop_data: dict) -> Union[str, dict]:
    #     #     # FIXME: use new function *generate_response_from_reference*
    #     #     # FIXME: Handle the reference
    #     #     v_ref = _YamlSchema.get_schema_ref(resp_prop_data)
    #     #     if strategy is ResponseStrategy.OBJECT:
    #     #         return {
    #     #             "name": "",
    #     #             # TODO: Set the *required* property correctly
    #     #             "required": True,
    #     #             # TODO: Set the *type* property correctly
    #     #             "type": "file",
    #     #             # TODO: Set the *format* property correctly
    #     #             "format": None,
    #     #             "items": [],
    #     #             "FIXME": "Handle the reference",
    #     #         }
    #     #     else:
    #     #         return "FIXME: Handle the reference"
    #     #
    #     # def _handle_not_ref_data(resp_prop_data: dict) -> Union[str, list, dict]:
    #     #
    #     #     def _handle_list_type_value_with_object_strategy(data: dict) -> dict:
    #     #         response_data_prop = {
    #     #             "name": "",
    #     #             # TODO: Set the *required* property correctly
    #     #             "required": True,
    #     #             "type": v_type,
    #     #             # TODO: Set the *format* property correctly
    #     #             "format": None,
    #     #             "items": [],
    #     #         }
    #     #
    #     #         single_response = _YamlSchema.get_schema_ref(data["items"])
    #     #         parser = self.schema_parser_factory.object(single_response)
    #     #         single_response_properties = parser.get_properties(default={})
    #     #         if single_response_properties:
    #     #             for item_k, item_v in parser.get_properties().items():
    #     #                 if _YamlSchema.has_ref(item_v):
    #     #                     # TODO: Should consider the algorithm to handle nested reference case
    #     #                     print("[WARNING] Not implement yet ...")
    #     #                 else:
    #     #                     item_type = convert_js_type(item_v["type"])
    #     #                     # TODO: Set the *required* property correctly
    #     #                     item = {"name": item_k, "required": True, "type": item_type}
    #     #                     assert isinstance(
    #     #                         response_data_prop["items"], list
    #     #                     ), "The data type of property *items* must be *list*."
    #     #                     response_data_prop["items"].append(item)
    #     #         return response_data_prop
    #     #
    #     #     def _handle_object_type_value_with_object_strategy(v_type: str) -> dict:
    #     #         # FIXME: handle the reference like object type
    #     #         return {
    #     #             "name": "",
    #     #             # TODO: Set the *required* property correctly
    #     #             "required": True,
    #     #             "type": v_type,
    #     #             # TODO: Set the *format* property correctly
    #     #             "format": None,
    #     #             "items": None,
    #     #         }
    #     #
    #     #     def _handle_other_types_value_with_object_strategy(v_type: str) -> dict:
    #     #         return {
    #     #             "name": "",
    #     #             # TODO: Set the *required* property correctly
    #     #             "required": True,
    #     #             "type": v_type,
    #     #             # TODO: Set the *format* property correctly
    #     #             "format": None,
    #     #             "items": None,
    #     #         }
    #     #
    #     #     def _handle_list_type_value_with_non_object_strategy(data: dict) -> list:
    #     #         single_response = _YamlSchema.get_schema_ref(data["items"])
    #     #         parser = self.schema_parser_factory.object(single_response)
    #     #         item = {}
    #     #         single_response_properties = parser.get_properties(default={})
    #     #         if single_response_properties:
    #     #             for item_k, item_v in parser.get_properties().items():
    #     #                 if _YamlSchema.has_ref(item_v):
    #     #                     # TODO: Should consider the algorithm to handle nested reference case
    #     #                     obj_item_type = convert_js_type(item_v["additionalProperties"]["type"])
    #     #                     print("[WARNING] Not implement yet ...")
    #     #                 else:
    #     #                     item_type = convert_js_type(item_v["type"])
    #     #                     if locate(item_type) is str:
    #     #                         # lowercase_letters = string.ascii_lowercase
    #     #                         # random_value = "".join([random.choice(lowercase_letters) for _ in range(5)])
    #     #                         random_value = "random string value"
    #     #                     elif locate(item_type) is int:
    #     #                         # random_value = int(
    #     #                         #     "".join([random.choice([f"{i}" for i in range(10)]) for _ in range(5)]))
    #     #                         random_value = "random integer value"
    #     #                     else:
    #     #                         raise NotImplementedError
    #     #                     item[item_k] = random_value
    #     #         return [item]
    #     #
    #     #     print(f"[DEBUG in _handle_not_ref_data] resp_prop_data: {resp_prop_data}")
    #     #     v_type = convert_js_type(resp_prop_data["type"])
    #     #     if strategy is ResponseStrategy.OBJECT:
    #     #         if locate(v_type) == list:
    #     #             return _handle_list_type_value_with_object_strategy(resp_prop_data)
    #     #         elif locate(v_type) == dict:
    #     #             return _handle_object_type_value_with_object_strategy(v_type)
    #     #         else:
    #     #             return _handle_other_types_value_with_object_strategy(v_type)
    #     #     else:
    #     #         if locate(v_type) == list:
    #     #             return _handle_list_type_value_with_non_object_strategy(resp_prop_data)
    #     #         elif locate(v_type) == dict:
    #     #             # FIXME: handle the reference like object type
    #     #             return "random object value"
    #     #         elif locate(v_type) == str:
    #     #             # lowercase_letters = string.ascii_lowercase
    #     #             # k_value = "".join([random.choice(lowercase_letters) for _ in range(5)])
    #     #             return "random string value"
    #     #         elif locate(v_type) == int:
    #     #             # k_value = int("".join([random.choice([f"{i}" for i in range(10)]) for _ in range(5)]))
    #     #             return "random integer value"
    #     #         elif locate(v_type) == bool:
    #     #             return "random boolean value"
    #     #         elif v_type == "file":
    #     #             # TODO: Handle the file download feature
    #     #             return "random file output stream"
    #     #         else:
    #     #             raise NotImplementedError
    #
    #     if not property_value:
    #         return strategy.generate_empty_response()
    #         # return _handle_empty_data()
    #     if _YamlSchema.has_ref(property_value):
    #         return strategy.generate_response_from_reference(_YamlSchema.get_schema_ref(property_value))
    #         # return _handle_ref_data(property_value)
    #     else:
    #         return strategy.generate_response_from_data(
    #             resp_prop_data=property_value,
    #             get_schema_parser_factory=ensure_get_schema_parser_factory,
    #             # has_ref_callback=_YamlSchema.has_ref,
    #             get_ref_callback=_YamlSchema.get_schema_ref,
    #         )
    #         # return _handle_not_ref_data(property_value)

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
