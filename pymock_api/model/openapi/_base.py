from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Union

from ..api_config import _Config
from ..enums import OpenAPIVersion
from ._parser_factory import BaseOpenAPISchemaParserFactory, get_schema_parser_factory
from ._schema_parser import BaseOpenAPISchemaParser

Self = Any

OpenAPI_Document_Version: OpenAPIVersion = OpenAPIVersion.V3
OpenAPI_Parser_Factory: BaseOpenAPISchemaParserFactory = get_schema_parser_factory(version=OpenAPI_Document_Version)


def get_openapi_version() -> OpenAPIVersion:
    global OpenAPI_Document_Version
    return OpenAPI_Document_Version


def set_openapi_version(v: Union[str, OpenAPIVersion]) -> None:
    global OpenAPI_Document_Version
    OpenAPI_Document_Version = OpenAPIVersion.to_enum(v)


def set_parser_factory(f: BaseOpenAPISchemaParserFactory) -> None:
    global OpenAPI_Parser_Factory
    OpenAPI_Parser_Factory = f


class BaseOpenAPIDataModel(metaclass=ABCMeta):

    @property
    def schema_parser_factory(self) -> BaseOpenAPISchemaParserFactory:
        global OpenAPI_Document_Version, OpenAPI_Parser_Factory
        assert (
            OpenAPI_Parser_Factory.chk_version(OpenAPI_Document_Version) is True
        ), "The parser factory is not mapping with the OpenAPI documentation version."
        return OpenAPI_Parser_Factory

    def load_schema_parser_factory_with_openapi_version(self) -> BaseOpenAPISchemaParserFactory:
        global OpenAPI_Document_Version
        return get_schema_parser_factory(version=OpenAPI_Document_Version)

    def reload_schema_parser_factory(self) -> None:
        self._load_schema_parser_factory()

    def _load_schema_parser_factory(self) -> None:
        set_parser_factory(self.load_schema_parser_factory_with_openapi_version())

    @classmethod
    def generate(cls, *args, **kwargs) -> Self:
        raise NotImplementedError

    @abstractmethod
    def deserialize(self, data: Dict) -> Self:
        pass


class Transferable(BaseOpenAPIDataModel):
    @abstractmethod
    def to_api_config(self, **kwargs) -> _Config:
        pass


ComponentDefinition: Dict[str, dict] = {}


def get_component_definition() -> Dict:
    global ComponentDefinition
    return ComponentDefinition


def set_component_definition(openapi_parser: BaseOpenAPISchemaParser) -> None:
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

        print(f"[DEBUG in get_schema_ref] data: {data}")
        _has_ref = _YamlSchema.has_ref(data)
        if not _has_ref:
            raise ValueError("This parameter has no ref in schema.")
        schema_path = (
            (data["schema"]["$ref"] if _has_ref == "schema" else data["$ref"]).replace("#/", "").split("/")[1:]
        )
        print(f"[DEBUG in get_schema_ref] schema_path: {schema_path}")
        # Operate the component definition object
        return _get_schema(get_component_definition(), schema_path, 0)
