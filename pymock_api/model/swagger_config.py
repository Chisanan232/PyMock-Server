import json
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List

from pymock_api.model.api_config import APIConfig
from pymock_api.model.api_config import APIParameter as PyMockAPIParameter
from pymock_api.model.api_config import BaseConfig, MockAPI, MockAPIs, _Config

Self = Any


def convert_js_type(t: str) -> str:
    if t == "string":
        return "str"
    elif t == "integer":
        return "int"
    elif t == "boolean":
        return "bool"
    elif t == "array":
        return "bool"
    else:
        raise TypeError(f"Currently, it cannot parse JS type '{t}'.")


ComponentDefinition: Dict[str, dict] = {}


def get_component_definition() -> Dict:
    global ComponentDefinition
    return ComponentDefinition


def set_component_definition(data: dict, key: str = "definitions") -> None:
    global ComponentDefinition
    ComponentDefinition = data.get(key, {})


class BaseSwaggerDataModel(metaclass=ABCMeta):
    @abstractmethod
    def deserialize(self, data: Dict) -> Self:
        pass


class Transferable(BaseSwaggerDataModel):
    @abstractmethod
    def to_api_config(self, **kwargs) -> _Config:
        pass


class Tag(BaseSwaggerDataModel):
    def __init__(self):
        self.name: str = ""
        self.description: str = ""

    def deserialize(self, data: Dict) -> "Tag":
        self.name = data["name"]
        self.description = data["description"]
        return self


class APIParameter(Transferable):
    def __init__(self):
        self.name: str = ""
        self.required: bool = False
        self.value_type: str = ""
        self.default: Any = None

    def deserialize(self, data: Dict) -> "APIParameter":
        print(f"[DEBUG in src] before handled, data: {data}")
        handled_data = self.parse_schema(data)
        print(f"[DEBUG in src] after handled, handled_data: {handled_data}")
        self.name = handled_data["name"]
        self.required = handled_data["required"]
        self.value_type = convert_js_type(handled_data["type"])
        self.default = handled_data.get("default", None)
        return self

    def to_api_config(self) -> PyMockAPIParameter:  # type: ignore[override]
        return PyMockAPIParameter(
            name=self.name,
            required=self.required,
            value_type=self.value_type,
            default=self.default,
            value_format=None,
        )

    def has_schema(self, data: Dict) -> bool:
        return data.get("schema", None) is not None

    def has_ref_in_schema(self, data: Dict) -> bool:
        if self.has_schema(data):
            return data["schema"].get("$ref", None) is not None
        return False

    def parse_schema(self, data: Dict, accept_no_schema: bool = True) -> dict:
        if not self.has_schema(data):
            if accept_no_schema:
                return data
            raise ValueError(f"This data '{data}' doesn't have key 'schema'.")

        if self.has_ref_in_schema(data):
            raise NotImplementedError
        else:
            return {
                "name": data["name"],
                "required": data["required"],
                "type": data["schema"]["type"],
                "default": data["schema"].get("default", None),
            }


class API(Transferable):
    def __init__(self):
        self.path: str = ""
        self.http_method: str = ""
        self.parameters: List[APIParameter] = []
        self.response: Dict = {}
        self.tags: List[str] = []

    def deserialize(self, data: Dict) -> "API":
        print(f"[DEBUG in API.deserialize] parsing: data: {data}")
        config_api_parameters = APIParameter()
        has_ref_in_schema_param = list(filter(config_api_parameters.has_ref_in_schema, data["parameters"]))
        if has_ref_in_schema_param:
            print("[DEBUG in src] has ref in schema")
            assert len(data["parameters"]) == 1
            handled_parameters = self._process_has_ref_parameters(data["parameters"][0])
        else:
            print("[DEBUG in src] does not has ref in schema")
            handled_parameters = data["parameters"]
        self.parameters = list(map(lambda p: APIParameter().deserialize(data=p), handled_parameters))
        # TODO: Process the response
        self.response = data["responses"]["200"]
        self.tags = data.get("tags", [])
        return self

    def _process_has_ref_parameters(self, data: Dict) -> List[dict]:
        def _get_schema(component_def_data: dict, paths: List[str], i: int) -> dict:
            if i == len(paths) - 1:
                return component_def_data[paths[i]]
            else:
                return _get_schema(component_def_data[paths[i]], paths, i + 1)

        config_api_parameters = APIParameter()
        if not config_api_parameters.has_ref_in_schema(data):
            raise ValueError("")

        schema_path = data["schema"]["$ref"].replace("#/", "").split("/")[1:]
        request_body_params = _get_schema(ComponentDefinition, schema_path, 0)
        print(f"[DEBUG ub src] request_body_params: {request_body_params}")
        # TODO: Should use the reference to get the details of parameters.
        parameters: List[dict] = []
        for param_name, param_props in request_body_params["properties"].items():
            parameters.append(
                {
                    "name": param_name,
                    "required": param_name in request_body_params["required"],
                    "type": param_props["type"],
                    "default": param_props.get("default", None),
                }
            )
        return parameters

    def to_api_config(self, base_url: str = "") -> MockAPI:  # type: ignore[override]
        mock_api = MockAPI(url=self.path.replace(base_url, ""))
        mock_api.set_request(
            method=self.http_method.upper(),
            parameters=list(map(lambda p: p.to_api_config(), self.parameters)),
        )
        mock_api.set_response(value=json.dumps(self.response))
        return mock_api


class SwaggerConfig(Transferable):
    def __init__(self):
        self.paths: List[API] = []
        self.tags: List[Tag] = []

    def deserialize(self, data: Dict) -> "SwaggerConfig":
        apis: dict = data["paths"]
        for api_path, api_props in apis.items():
            print(f"[DEBUG in SwaggerConfig.deserialize] first layer parsing: api_props: {api_props}")
            for one_api_http_method, one_api_details in api_props.items():
                print(f"[DEBUG in SwaggerConfig.deserialize] second layer parsing: one_api_details: {one_api_details}")
                api = API().deserialize(data=one_api_details)
                api.path = api_path
                api.http_method = one_api_http_method
                self.paths.append(api)

        tags: List[dict] = data.get("tags", [])
        self.tags = list(map(lambda t: Tag().deserialize(t), tags))

        global ComponentDefinition
        ComponentDefinition = data.get("definitions", {})

        return self

    def to_api_config(self, base_url: str = "") -> APIConfig:  # type: ignore[override]
        api_config = APIConfig(name="", description="", apis=MockAPIs(base=BaseConfig(url=base_url), apis={}))
        assert api_config.apis is not None and api_config.apis.apis == {}
        for swagger_api in self.paths:
            api_config.apis.apis[
                swagger_api.path.replace(base_url, "")[1:].replace("/", "_")
            ] = swagger_api.to_api_config(base_url=base_url)
        return api_config
