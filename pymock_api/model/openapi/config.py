from abc import ABCMeta, abstractmethod
from pydoc import locate
from typing import Any, Dict, List, Optional, Union

from .. import APIConfig, MockAPI, MockAPIs
from ..api_config import BaseConfig, _Config
from ..api_config.apis import APIParameter as PyMockAPIParameter
from ..enums import ResponseStrategy
from ._parse import OpenAPIParser, OpenAPIPathParser
from ._parser_factory import OpenAPIParserFactory

Self = Any


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


ComponentDefinition: Dict[str, dict] = {}


def get_component_definition() -> Dict:
    global ComponentDefinition
    return ComponentDefinition


def set_component_definition(openapi_parser: OpenAPIParser) -> None:
    global ComponentDefinition
    ComponentDefinition = openapi_parser.get_objects()


class _YamlSchema:
    @classmethod
    def has_schema(cls, data: Dict) -> bool:
        return data.get("schema", None) is not None

    @classmethod
    def has_ref(cls, data: Dict) -> str:
        if cls.has_schema(data):
            has_schema_ref = data["schema"].get("$ref", None) is not None
            return "schema" if has_schema_ref else ""
        else:
            _has_ref = data.get("$ref", None) is not None
            return "ref" if _has_ref else ""

    @classmethod
    def get_schema_ref(cls, data: dict) -> dict:
        def _get_schema(component_def_data: dict, paths: List[str], i: int) -> dict:
            if i == len(paths) - 1:
                return component_def_data[paths[i]]
            else:
                return _get_schema(component_def_data[paths[i]], paths, i + 1)

        _has_ref = _YamlSchema.has_ref(data)
        if not _has_ref:
            raise ValueError("This parameter has no ref in schema.")
        schema_path = (
            (data["schema"]["$ref"] if _has_ref == "schema" else data["$ref"]).replace("#/", "").split("/")[1:]
        )
        # Operate the component definition object
        return _get_schema(get_component_definition(), schema_path, 0)


class BaseSwaggerDataModel(metaclass=ABCMeta):

    def __init__(self):
        self._config_parser_factory: OpenAPIParserFactory = OpenAPIParserFactory()

    @abstractmethod
    def deserialize(self, data: Dict) -> Self:
        pass


class Transferable(BaseSwaggerDataModel):
    @abstractmethod
    def to_api_config(self, **kwargs) -> _Config:
        pass


class Tag(BaseSwaggerDataModel):
    def __init__(self):
        super().__init__()
        self.name: str = ""
        self.description: str = ""

    def deserialize(self, data: Dict) -> "Tag":
        parser = self._config_parser_factory.tag(data)
        self.name = parser.get_name()
        self.description = parser.get_description()
        return self


class APIParameter(Transferable):
    def __init__(self):
        super().__init__()
        self.name: str = ""
        self.required: bool = False
        self.value_type: str = ""
        self.default: Any = None
        self.items: Optional[list] = None

    def deserialize(self, data: Dict) -> "APIParameter":
        handled_data = self.parse_schema(data)
        self.name = handled_data["name"]
        self.required = handled_data["required"]
        self.value_type = convert_js_type(handled_data["type"])
        self.default = handled_data.get("default", None)
        items = handled_data.get("items", None)
        if items is not None:
            self.items = items if isinstance(items, list) else [items]
        return self

    def to_api_config(self) -> PyMockAPIParameter:  # type: ignore[override]
        return PyMockAPIParameter(
            name=self.name,
            required=self.required,
            value_type=self.value_type,
            default=self.default,
            value_format=None,
            items=self.items,
        )

    def parse_schema(self, data: Dict, accept_no_schema: bool = True) -> dict:
        if not _YamlSchema.has_schema(data):
            if accept_no_schema:
                return data
            raise ValueError(f"This data '{data}' doesn't have key 'schema'.")

        if _YamlSchema.has_ref(data):
            raise NotImplementedError
        else:
            parser = self._config_parser_factory.request_parameters(data)
            return {
                "name": parser.get_name(),
                "required": parser.get_required(),
                "type": parser.get_type(),
                "default": parser.get_default(),
            }


class API(Transferable):
    def __init__(self):
        super().__init__()
        self.path: str = ""
        self.http_method: str = ""
        self.parameters: List[APIParameter] = []
        self.response: Dict = {}
        self.tags: List[str] = []

        self.process_response_strategy: ResponseStrategy = ResponseStrategy.OBJECT

    def deserialize(self, data: Dict) -> "API":
        # FIXME: Does it have better way to set the HTTP response strategy?
        if not self.process_response_strategy:
            raise ValueError("Please set the strategy how it should process HTTP response.")
        openapi_path_parser = self._config_parser_factory.path(data=data)
        self.parameters = self._process_api_params(openapi_path_parser.get_request_parameters())
        self.response = self._process_response(openapi_path_parser, self.process_response_strategy)
        self.tags = openapi_path_parser.get_all_tags()
        return self

    def _process_api_params(self, params_data: List[dict]) -> List["APIParameter"]:
        has_ref_in_schema_param = list(filter(lambda p: _YamlSchema.has_ref(p) != "", params_data))
        if has_ref_in_schema_param:
            # TODO: Ensure the value maps this condition is really only one
            assert len(params_data) == 1
            handled_parameters = self._process_has_ref_parameters(params_data[0])
        else:
            # TODO: Parsing the data type of key *items* should be valid type of Python realm
            for param in params_data:
                parser = self._config_parser_factory.request_parameters(param)
                items = parser.get_items()
                if items is not None:
                    param["items"]["type"] = ensure_type_is_python_type(param["items"]["type"])
            handled_parameters = params_data
        return list(map(lambda p: APIParameter().deserialize(data=p), handled_parameters))

    def _process_has_ref_parameters(self, data: Dict) -> List[dict]:
        request_body_params = _YamlSchema.get_schema_ref(data)
        # TODO: Should use the reference to get the details of parameters.
        parameters: List[dict] = []
        parser = self._config_parser_factory.object(request_body_params)
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
                items_parser = self._config_parser_factory.object(items)
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

    def _process_response(self, openapi_path_parser: OpenAPIPathParser, strategy: ResponseStrategy) -> dict:
        assert openapi_path_parser.exist_in_response(status_code="200") is True
        status_200_response = openapi_path_parser.get_response(status_code="200")
        if strategy is ResponseStrategy.OBJECT:
            response_data = {
                "strategy": strategy,
                "data": [],
            }
        else:
            response_data = {
                "strategy": strategy,
                "data": {},
            }
        if _YamlSchema.has_schema(status_200_response):
            response_schema = _YamlSchema.get_schema_ref(status_200_response)
            parser = self._config_parser_factory.object(response_schema)
            response_schema_properties: Optional[dict] = parser.get_properties(default=None)
            if response_schema_properties:
                for k, v in response_schema_properties.items():
                    if strategy is ResponseStrategy.OBJECT:
                        response_data_prop = self._process_response_value(property_value=v, strategy=strategy)
                        assert isinstance(response_data_prop, dict)
                        response_data_prop["name"] = k
                        response_data_prop["required"] = k in parser.get_required(default=[k])
                        assert isinstance(
                            response_data["data"], list
                        ), "The response data type must be *list* if its HTTP response strategy is object."
                        response_data["data"].append(response_data_prop)
                    else:
                        assert isinstance(
                            response_data["data"], dict
                        ), "The response data type must be *dict* if its HTTP response strategy is not object."
                        response_data["data"][k] = self._process_response_value(property_value=v, strategy=strategy)
        else:
            resp_parser = self._config_parser_factory.response(status_200_response)
            assert resp_parser.exist_in_content(value_format="application/json") is True
            response_schema = resp_parser.get_content(value_format="application/json")
            if response_schema:
                raise NotImplementedError("Not support set HTTP response by this way in current version.")
        return response_data

    def _process_response_value(self, property_value: dict, strategy: ResponseStrategy) -> Union[str, dict]:
        if _YamlSchema.has_ref(property_value):
            # FIXME: Handle the reference
            v_ref = _YamlSchema.get_schema_ref(property_value)
            if strategy is ResponseStrategy.OBJECT:
                return {
                    "name": "",
                    # TODO: Set the *required* property correctly
                    "required": True,
                    # TODO: Set the *type* property correctly
                    "type": "file",
                    # TODO: Set the *format* property correctly
                    "format": None,
                    "items": [],
                    "FIXME": "Handle the reference",
                }
            else:
                k_value = "FIXME: Handle the reference"
        else:
            v_type = convert_js_type(property_value["type"])
            if strategy is ResponseStrategy.OBJECT:
                if locate(v_type) == list:
                    response_data_prop = {
                        "name": "",
                        # TODO: Set the *required* property correctly
                        "required": True,
                        "type": v_type,
                        # TODO: Set the *format* property correctly
                        "format": None,
                        "items": [],
                    }

                    single_response = _YamlSchema.get_schema_ref(property_value["items"])
                    parser = self._config_parser_factory.object(single_response)
                    single_response_properties = parser.get_properties(default={})
                    if single_response_properties:
                        for item_k, item_v in parser.get_properties().items():
                            item_type = convert_js_type(item_v["type"])
                            # TODO: Set the *required* property correctly
                            item = {"name": item_k, "required": True, "type": item_type}
                            assert isinstance(
                                response_data_prop["items"], list
                            ), "The data type of property *items* must be *list*."
                            response_data_prop["items"].append(item)
                    return response_data_prop
                else:
                    return {
                        "name": "",
                        # TODO: Set the *required* property correctly
                        "required": True,
                        "type": v_type,
                        # TODO: Set the *format* property correctly
                        "format": None,
                        "items": None,
                    }
            else:
                if locate(v_type) == list:
                    single_response = _YamlSchema.get_schema_ref(property_value["items"])
                    parser = self._config_parser_factory.object(single_response)
                    item = {}
                    single_response_properties = parser.get_properties(default={})
                    if single_response_properties:
                        for item_k, item_v in parser.get_properties().items():
                            item_type = convert_js_type(item_v["type"])
                            if locate(item_type) is str:
                                # lowercase_letters = string.ascii_lowercase
                                # random_value = "".join([random.choice(lowercase_letters) for _ in range(5)])
                                random_value = "random string value"
                            elif locate(item_type) is int:
                                # random_value = int(
                                #     "".join([random.choice([f"{i}" for i in range(10)]) for _ in range(5)]))
                                random_value = "random integer value"
                            else:
                                raise NotImplementedError
                            item[item_k] = random_value
                    k_value = [item]  # type: ignore[assignment]
                elif locate(v_type) == str:
                    # lowercase_letters = string.ascii_lowercase
                    # k_value = "".join([random.choice(lowercase_letters) for _ in range(5)])
                    k_value = "random string value"
                elif locate(v_type) == int:
                    # k_value = int("".join([random.choice([f"{i}" for i in range(10)]) for _ in range(5)]))
                    k_value = "random integer value"
                elif locate(v_type) == bool:
                    k_value = "random boolean value"
                elif v_type == "file":
                    # TODO: Handle the file download feature
                    k_value = "random file output stream"
                else:
                    raise NotImplementedError
        return k_value

    def to_api_config(self, base_url: str = "") -> MockAPI:  # type: ignore[override]
        mock_api = MockAPI(url=self.path.replace(base_url, ""), tag=self.tags[0] if self.tags else "")
        mock_api.set_request(
            method=self.http_method.upper(),
            parameters=list(map(lambda p: p.to_api_config(), self.parameters)),
        )
        resp_strategy = self.response["strategy"]
        if resp_strategy is ResponseStrategy.OBJECT:
            mock_api.set_response(strategy=resp_strategy, iterable_value=self.response["data"])
        else:
            mock_api.set_response(strategy=resp_strategy, value=self.response["data"])
        return mock_api


class SwaggerConfig(Transferable):
    def __init__(self):
        super().__init__()
        self.paths: List[API] = []
        self.tags: List[Tag] = []

    def deserialize(self, data: Dict) -> "SwaggerConfig":
        openapi_parser = self._config_parser_factory.entire_config(data=data)
        apis = openapi_parser.get_paths()
        for api_path, api_props in apis.items():
            for one_api_http_method, one_api_details in api_props.items():
                api = API().deserialize(data=one_api_details)
                api.path = api_path
                api.http_method = one_api_http_method
                self.paths.append(api)

        tags: List[dict] = openapi_parser.get_tags()
        self.tags = list(map(lambda t: Tag().deserialize(t), tags))

        set_component_definition(openapi_parser)

        return self

    def to_api_config(self, base_url: str = "") -> APIConfig:  # type: ignore[override]
        api_config = APIConfig(name="", description="", apis=MockAPIs(base=BaseConfig(url=base_url), apis={}))
        assert api_config.apis is not None and api_config.apis.apis == {}
        for swagger_api in self.paths:
            base_url = self._align_url_format(base_url, swagger_api)
            api_config.apis.apis[self._generate_api_key(base_url, swagger_api)] = swagger_api.to_api_config(
                base_url=base_url
            )
        return api_config

    def _align_url_format(self, base_url: str, swagger_api: API) -> str:
        if swagger_api.path[0] != "/":
            swagger_api.path = f"/{swagger_api.path}"
        if base_url and base_url[0] != "/":
            base_url = f"/{base_url}"
        return base_url

    def _generate_api_key(self, base_url: str, swagger_api: API) -> str:
        return "_".join([swagger_api.http_method, swagger_api.path.replace(base_url, "")[1:].replace("/", "_")])
