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
    else:
        raise TypeError(f"Currently, it cannot parse JS type '{t}'.")


ComponentDefinition: Dict[str, dict] = {}


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
        def _get_schema(component_def_data: dict, paths: List[str], i: int) -> dict:
            if i == len(paths) - 1:
                return component_def_data[paths[i]]
            else:
                return _get_schema(component_def_data[paths[i]], paths, i + 1)

        if "schema" in data.keys():
            if "$ref" in data["schema"].keys():
                schema_path = data["schema"]["$ref"].replace("#/", "").split("/")
                request_body_params = _get_schema(ComponentDefinition, schema_path, 0)
                request_body_params
            else:
                self.name = data["name"]
                self.required = data["required"]
                self.value_type = convert_js_type(data["schema"]["type"])
                self.default = data["schema"]["default"]
        else:
            self.name = data["name"]
            self.required = data["required"]
            self.value_type = convert_js_type(data["type"])
            self.default = data.get("default", None)
        return self

    def to_api_config(self) -> PyMockAPIParameter:  # type: ignore[override]
        return PyMockAPIParameter(
            name=self.name,
            required=self.required,
            value_type=self.value_type,
            default=self.default,
            value_format=None,
        )


class API(Transferable):
    def __init__(self):
        self.path: str = ""
        self.http_method: str = ""
        self.parameters: List[APIParameter] = []
        self.response: Dict = {}
        self.tags: List[str] = []

    def deserialize(self, data: Dict) -> "API":
        for http_method, http_info in data.items():
            self.http_method = http_method
            self.parameters = list(map(lambda p: APIParameter().deserialize(data=p), http_info["parameters"]))
            # TODO: Process the response
            self.response = http_info["responses"]["200"]["content"]["application/json"]["schema"]
            self.tags = data.get("tags", [])
        return self

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
            api = API().deserialize(data=api_props)
            api.path = api_path
            self.paths.append(api)

        tags: List[dict] = data.get("tags", [])
        self.tags = list(map(lambda t: Tag().deserialize(t), tags))

        set_component_definition(data)

        return self

    def to_api_config(self, base_url: str = "") -> APIConfig:  # type: ignore[override]
        api_config = APIConfig(name="", description="", apis=MockAPIs(base=BaseConfig(url=base_url), apis={}))
        assert api_config.apis is not None and api_config.apis.apis == {}
        for swagger_api in self.paths:
            api_config.apis.apis[
                swagger_api.path.replace(base_url, "")[1:].replace("/", "_")
            ] = swagger_api.to_api_config(base_url=base_url)
        return api_config
