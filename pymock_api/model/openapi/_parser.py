from typing import Dict, List, Optional, Type

from ..enums import OpenAPIVersion
from ._base import (
    BaseOpenAPIDataModel,
    _YamlSchema,
    ensure_get_schema_parser_factory,
    get_openapi_version,
)
from ._parser_factory import BaseOpenAPISchemaParserFactory
from ._schema_parser import BaseOpenAPIPathSchemaParser, BaseOpenAPISchemaParser


def convert_js_type(t: str) -> str:
    if t == "string":
        return "str"
    elif t in ["integer", "number"]:
        return "int"
    elif t == "boolean":
        return "bool"
    elif t == "array":
        return "list"
    elif t == "file":
        return "file"
    else:
        raise TypeError(f"Currently, it cannot parse JS type '{t}'.")


# TODO: Should clean the parsing process
def ensure_type_is_python_type(t: str) -> str:
    if t in ["string", "integer", "number", "boolean", "array"]:
        return convert_js_type(t)
    return t


class APIParser:
    def __init__(self, parser: BaseOpenAPIPathSchemaParser):
        self.parser = parser

    @property
    def schema_parser_factory(self) -> BaseOpenAPISchemaParserFactory:
        return ensure_get_schema_parser_factory()

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

    def process_responses(self):
        pass

    def process_tags(self):
        pass


class OpenAPIDocumentConfigParser:

    def __init__(self, parser: BaseOpenAPISchemaParser):
        self.parser = parser

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
