from typing import Dict, List, Optional

from ._base_schema_parser import (
    BaseOpenAPIPathSchemaParser,
    BaseOpenAPIRequestParameterItemSchemaParser,
    BaseOpenAPIResponseSchemaParser,
    BaseOpenAPISchemaParser,
    BaseOpenAPITagSchemaParser,
)


class OpenAPIResponseSchemaParser(BaseOpenAPIResponseSchemaParser):

    def get_content(self, value_format: str) -> Dict[str, dict]:
        return self._data["content"][value_format]["schema"]

    def exist_in_content(self, value_format: str) -> bool:
        return value_format in self._data["content"].keys()


class OpenAPIRequestParameterItemSchemaParser(BaseOpenAPIRequestParameterItemSchemaParser):

    def get_items_type(self) -> Optional[str]:
        return self._data.get("type", None)

    def set_items_type(self, value_type: str) -> None:
        self._data["type"] = value_type


class OpenAPIV2PathSchemaParser(BaseOpenAPIPathSchemaParser):

    def get_request_parameters(self) -> List[dict]:
        return self._data.get("parameters", [])

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


class OpenAPITagSchemaParser(BaseOpenAPITagSchemaParser):

    def get_name(self):
        return self._data["name"]

    def get_description(self):
        return self._data["description"]


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
