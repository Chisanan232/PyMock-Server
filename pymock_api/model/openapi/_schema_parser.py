import json
import pathlib
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Optional


class BaseSchemaParser(metaclass=ABCMeta):
    def __init__(self, data: dict):
        self._data = data


class BaseOpenAPIObjectSchemaParser(BaseSchemaParser):

    @abstractmethod
    def get_required(self, default: Any = None) -> List[str]:
        pass

    @abstractmethod
    def get_properties(self, default: Any = None) -> Dict[str, dict]:
        pass


class OpenAPIObjectSchemaParser(BaseOpenAPIObjectSchemaParser):

    def get_required(self, default: Any = None) -> List[str]:
        if default is not None:
            return self._data.get("required", default)
        else:
            return self._data.get("required", [])

    def get_properties(self, default: Any = None) -> Dict[str, dict]:
        if default is not None:
            return self._data.get("properties", default)
        else:
            return self._data["properties"]


class BaseOpenAPIResponseSchemaParser(BaseSchemaParser):

    @abstractmethod
    def get_content(self, value_format: str) -> Dict[str, dict]:
        pass

    @abstractmethod
    def exist_in_content(self, value_format: str) -> bool:
        pass


class OpenAPIResponseSchemaParser(BaseOpenAPIResponseSchemaParser):

    def get_content(self, value_format: str) -> Dict[str, dict]:
        return self._data["content"][value_format]["schema"]

    def exist_in_content(self, value_format: str) -> bool:
        return value_format in self._data["content"].keys()


class BaseOpenAPIRequestParametersSchemaParser(BaseSchemaParser):

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_required(self) -> str:
        pass

    @abstractmethod
    def get_type(self) -> str:
        pass

    @abstractmethod
    def get_default(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_items(self):
        pass


class OpenAPIRequestParametersSchemaParser(BaseOpenAPIRequestParametersSchemaParser):

    def get_name(self) -> str:
        return self._data["name"]

    def get_required(self) -> str:
        return self._data["required"]

    def get_type(self) -> str:
        return self._data["schema"]["type"]

    def get_default(self) -> Optional[str]:
        return self._data["schema"].get("default", None)

    def get_items(self):
        return self._data.get("items", None)


class BaseOpenAPIPathSchemaParser(BaseSchemaParser):

    @abstractmethod
    def get_request_parameters(self) -> List[dict]:
        pass

    def get_request_body(self, value_format: str = "application/json") -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_response(self, status_code: str) -> dict:
        pass

    @abstractmethod
    def exist_in_response(self, status_code: str) -> bool:
        pass

    @abstractmethod
    def get_all_tags(self) -> List[str]:
        pass


class OpenAPIV2PathSchemaParser(BaseOpenAPIPathSchemaParser):

    def get_request_parameters(self) -> List[dict]:
        return self._data["parameters"]

    def get_response(self, status_code: str) -> dict:
        return self._data["responses"][status_code]

    def exist_in_response(self, status_code: str) -> bool:
        return status_code in self._data["responses"].keys()

    def get_all_tags(self) -> List[str]:
        return self._data.get("tags", [])


class OpenAPIV3PathSchemaParser(BaseOpenAPIPathSchemaParser):

    def get_request_parameters(self) -> List[dict]:
        return self._data.get("parameters", [])

    def get_request_body(self, value_format: str = "application/json") -> dict:
        if "requestBody" in self._data.keys():
            return self._data["requestBody"]["content"][value_format]
        return {}

    def get_response(self, status_code: str) -> dict:
        return self._data["responses"][status_code]

    def exist_in_response(self, status_code: str) -> bool:
        return status_code in self._data["responses"].keys()

    def get_all_tags(self) -> List[str]:
        return self._data.get("tags", [])


class BaseOpenAPITagSchemaParser(BaseSchemaParser):

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_description(self):
        pass


class OpenAPITagSchemaParser(BaseOpenAPITagSchemaParser):

    def get_name(self):
        return self._data["name"]

    def get_description(self):
        return self._data["description"]


class BaseOpenAPISchemaParser(BaseSchemaParser):

    def __init__(self, file: str = "", data: Dict = {}):
        super().__init__(data=data)

        if file:
            file_path = pathlib.Path(file)
            if not file_path.exists():
                raise FileNotFoundError(f"Cannot find the OpenAPI format configuration at file path *{file_path}*.")
            with open(str(file_path), "r", encoding="utf-8") as io_stream:
                self._data = json.load(io_stream)

        assert self._data, "No any data. Parse OpenAPI config fail."

    @abstractmethod
    def get_paths(self) -> Dict[str, Dict]:
        pass

    @abstractmethod
    def get_tags(self) -> List[dict]:
        pass

    @abstractmethod
    def get_objects(self) -> Dict[str, dict]:
        pass


class OpenAPIV2SchemaParser(BaseOpenAPISchemaParser):

    def get_paths(self) -> Dict[str, Dict]:
        return self._data["paths"]

    def get_tags(self) -> List[dict]:
        return self._data.get("tags", [])

    def get_objects(self) -> Dict[str, dict]:
        return self._data.get("definitions", {})


class OpenAPIV3SchemaParser(BaseOpenAPISchemaParser):

    def get_paths(self) -> Dict[str, Dict]:
        return self._data["paths"]

    def get_tags(self) -> List[dict]:
        # Not support this property in OpenAPI v3
        return []

    def get_objects(self) -> Dict[str, dict]:
        return self._data.get("components", {})
