from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List

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


class BaseSwaggerDataModel(metaclass=ABCMeta):
    @abstractmethod
    def deserialize(self, data: Dict) -> Self:
        pass


class APIParameter(BaseSwaggerDataModel):
    name: str = ""
    required: bool = False
    value_type: str = ""
    default_value: Any = None

    def deserialize(self, data: Dict) -> "APIParameter":
        self.name = data["name"]
        self.required = data["required"]
        self.value_type = convert_js_type(data["schema"]["type"])
        self.default_value = data["schema"]["default"]
        return self


class API(BaseSwaggerDataModel):
    path: str = ""
    http_method: str = ""
    parameters: List[APIParameter] = []
    response: Dict = {}

    def deserialize(self, data: Dict) -> "API":
        for http_method, http_info in data.items():
            self.http_method = http_method
            self.parameters = list(map(lambda p: APIParameter().deserialize(data=p), http_info["parameters"]))
            # TODO: Process the response
            self.response = http_info["responses"]
        return self


class SwaggerConfig(BaseSwaggerDataModel):
    paths: List[API] = []

    def deserialize(self, data: Dict) -> "SwaggerConfig":
        apis: dict = data["paths"]
        for api_path, api_props in apis.items():
            api = API().deserialize(data=api_props)
            api.path = api_path
            self.paths.append(api)
        return self