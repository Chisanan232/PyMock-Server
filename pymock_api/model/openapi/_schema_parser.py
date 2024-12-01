from typing import Any, Dict, List, Optional

from ._base_schema_parser import (
    BaseOpenAPIObjectSchemaParser,
    BaseOpenAPIPathSchemaParser,
    BaseOpenAPIRequestParameterItemSchemaParser,
    BaseOpenAPIRequestParametersSchemaParser,
    BaseOpenAPIResponseSchemaParser,
    BaseOpenAPISchemaParser,
    BaseOpenAPITagSchemaParser,
)
from ._tmp_data_model import get_component_definition


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


class _ReferenceObjectParser:
    @classmethod
    def has_schema(cls, data: Dict) -> bool:
        return data.get("schema", None) is not None

    @classmethod
    def has_additional_properties(cls, data: Dict) -> bool:
        return data.get("additionalProperties", None) is not None

    @classmethod
    def has_ref(cls, data: Dict) -> str:
        if cls.has_schema(data):
            has_schema_ref = data["schema"].get("$ref", None) is not None
            return "schema" if has_schema_ref else ""
        elif cls.has_additional_properties(data):
            has_additional_properties = data["additionalProperties"].get("$ref", None) is not None
            return "additionalProperties" if has_additional_properties else ""
        else:
            _has_ref = data.get("$ref", None) is not None
            return "ref" if _has_ref else ""

    @classmethod
    def get_schema_ref(cls, data: dict, accept_no_ref: bool = False) -> dict:
        def _get_schema(component_def_data: dict, paths: List[str], i: int) -> dict:
            if i == len(paths) - 1:
                return component_def_data[paths[i]]
            else:
                return _get_schema(component_def_data[paths[i]], paths, i + 1)

        print(f"[DEBUG in get_schema_ref] data: {data}")
        _has_ref = _ReferenceObjectParser.has_ref(data)
        if not _has_ref:
            if accept_no_ref:
                return {}
            raise ValueError("This parameter has no ref in schema.")
        schema_path = (data[_has_ref]["$ref"] if _has_ref != "ref" else data["$ref"]).replace("#/", "").split("/")[1:]
        print(f"[DEBUG in get_schema_ref] schema_path: {schema_path}")
        # Operate the component definition object
        return _get_schema(get_component_definition(), schema_path, 0)
