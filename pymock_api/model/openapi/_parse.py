import json
import pathlib
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Optional


class BaseOpenAPIObjectParser(metaclass=ABCMeta):

    def __init__(self, data: dict):
        self._data = data

    @abstractmethod
    def get_required(self, default: Any = None) -> List[str]:
        pass

    @abstractmethod
    def get_properties(self, default: Any = None) -> Dict[str, dict]:
        pass


class OpenAPIObjectParser(BaseOpenAPIObjectParser):

    def get_required(self, default: Any = None) -> List[str]:
        if default is not None:
            return self._data.get("required", default)
        else:
            return self._data["required"]

    def get_properties(self, default: Any = None) -> Dict[str, dict]:
        if default is not None:
            return self._data.get("properties", default)
        else:
            return self._data["properties"]


class BaseOpenAPIResponseParser(metaclass=ABCMeta):

    def __init__(self, data: dict):
        self._data = data

    @abstractmethod
    def get_content(self, value_format: str) -> Dict[str, dict]:
        pass

    @abstractmethod
    def exist_in_content(self, value_format: str) -> bool:
        pass


class OpenAPIResponseParser(BaseOpenAPIResponseParser):

    def get_content(self, value_format: str) -> Dict[str, dict]:
        return self._data["content"][value_format]["schema"]

    def exist_in_content(self, value_format: str) -> bool:
        return value_format in self._data["content"].keys()


class BaseOpenAPIRequestParametersParser(metaclass=ABCMeta):

    def __init__(self, data: dict):
        self._data = data

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


class OpenAPIRequestParametersParser(BaseOpenAPIRequestParametersParser):

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


class BaseOpenAPIPathParser(metaclass=ABCMeta):

    def __init__(self, data: dict):
        self._data = data

    @abstractmethod
    def get_request_parameters(self) -> List[dict]:
        pass

    @abstractmethod
    def get_response(self, status_code: str) -> dict:
        pass

    @abstractmethod
    def exist_in_response(self, status_code: str) -> bool:
        pass

    @abstractmethod
    def get_all_tags(self) -> List[str]:
        pass


class OpenAPIPathParser(BaseOpenAPIPathParser):

    def get_request_parameters(self) -> List[dict]:
        return self._data["parameters"]

    def get_response(self, status_code: str) -> dict:
        return self._data["responses"][status_code]

    def exist_in_response(self, status_code: str) -> bool:
        return status_code in self._data["responses"].keys()

    def get_all_tags(self) -> List[str]:
        return self._data.get("tags", [])


class BaseOpenAPITagParser(metaclass=ABCMeta):

    def __init__(self, data: dict):
        self._data = data

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_description(self):
        pass


class OpenAPITagParser(BaseOpenAPITagParser):

    def get_name(self):
        return self._data["name"]

    def get_description(self):
        return self._data["description"]


class BaseOpenAPIParser(metaclass=ABCMeta):

    def __init__(self, file: str = "", data: Dict = {}):
        if file:
            file_path = pathlib.Path(file)
            if not file_path.exists():
                raise FileNotFoundError(f"Cannot find the OpenAPI format configuration at file path *{file_path}*.")
            with open(str(file_path), "r", encoding="utf-8") as io_stream:
                self._data = json.load(io_stream)

        if data:
            self._data = data

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


class OpenAPIParser(BaseOpenAPIParser):

    def get_paths(self) -> Dict[str, Dict]:
        return self._data["paths"]

    def get_tags(self) -> List[dict]:
        return self._data.get("tags", [])

    def get_objects(self) -> Dict[str, dict]:
        return self._data.get("definitions", {})


class OpenAPIV3Parser(BaseOpenAPIParser):

    def get_paths(self) -> Dict[str, Dict]:
        return self._data["paths"]

    def get_tags(self) -> List[dict]:
        # Not support this property in OpenAPI v3
        return []

    def get_objects(self) -> Dict[str, dict]:
        return self._data.get("components", {}).get("schemas", {})
