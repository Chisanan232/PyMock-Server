import json
import pathlib
from typing import Any, Dict, List, Optional


class OpenAPIObjectParser:

    def __init__(self, data: dict):
        self._data = data

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


class OpenAPIResponseParser:

    def __init__(self, data: dict):
        self._data = data

    def get_content(self, value_format: str) -> Dict[str, dict]:
        return self._data["content"][value_format]["schema"]

    def exist_in_content(self, value_format: str) -> bool:
        return value_format in self._data["content"].keys()


class OpenAPIRequestParametersParser:

    def __init__(self, data: dict):
        self._data = data

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


class OpenAPIPathParser:

    def __init__(self, data: dict):
        self._data = data

    def get_request_parameters(self) -> List[dict]:
        return self._data["parameters"]

    def get_response(self, status_code: str) -> dict:
        return self._data["responses"][status_code]

    def exist_in_response(self, status_code: str) -> bool:
        return status_code in self._data["responses"].keys()

    def get_all_tags(self) -> List[str]:
        return self._data.get("tags", [])


class OpenAPITagParser:

    def __init__(self, data: dict):
        self._data = data

    def get_name(self):
        return self._data["name"]

    def get_description(self):
        return self._data["description"]


class OpenAPIParser:

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

    def get_paths(self) -> Dict[str, Dict]:
        return self._data["paths"]

    def get_tags(self) -> List[dict]:
        return self._data.get("tags", [])

    def get_objects(self) -> Dict[str, dict]:
        return self._data.get("definitions", {})


class OpenAPIParserFactory:

    def entire_api(self, file: str = "", data: Dict = {}) -> OpenAPIParser:
        return OpenAPIParser(file=file, data=data)

    def tag(self, data: Dict) -> OpenAPITagParser:
        return OpenAPITagParser(data=data)

    def path(self, data: Dict) -> OpenAPIPathParser:
        return OpenAPIPathParser(data=data)

    def request_parameters(self, data: Dict) -> OpenAPIRequestParametersParser:
        return OpenAPIRequestParametersParser(data=data)

    def response(self, data: Dict) -> OpenAPIResponseParser:
        return OpenAPIResponseParser(data=data)

    def object(self, data: Dict) -> OpenAPIObjectParser:
        return OpenAPIObjectParser(data=data)
