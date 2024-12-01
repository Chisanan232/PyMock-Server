from dataclasses import dataclass, field
from typing import Dict, List, Optional, cast

from .. import APIConfig, MockAPIs
from ..api_config import BaseConfig
from ._base import BaseOpenAPIDataModel, Transferable, set_openapi_version
from ._parser import OpenAPIDocumentConfigParser
from ._tmp_data_model import TmpAPIConfig, set_component_definition


@dataclass
class Tag(BaseOpenAPIDataModel):
    name: str = field(default_factory=str)
    description: str = field(default_factory=str)

    @classmethod
    def generate(cls, detail: dict) -> "Tag":
        return Tag().deserialize(data=detail)

    def deserialize(self, data: Dict) -> "Tag":
        parser = self.schema_parser_factory.tag(data)
        self.name = parser.get_name()
        self.description = parser.get_description()
        return self


@dataclass
class OpenAPIDocumentConfig(Transferable):
    paths: Dict[str, TmpAPIConfig] = field(default_factory=dict)
    tags: List[Tag] = field(default_factory=list)

    def deserialize(self, data: Dict) -> "OpenAPIDocumentConfig":
        self._chk_version_and_load_parser(data)

        openapi_schema_parser = self.schema_parser_factory.entire_config(data=data)
        set_component_definition(openapi_schema_parser)
        parser = OpenAPIDocumentConfigParser(parser=openapi_schema_parser)
        for path, config in data.get("paths", {}).items():
            self.paths[path] = TmpAPIConfig().deserialize(config)
        self.tags = cast(List[Tag], parser.process_tags(data_modal=Tag))

        return self

    def _chk_version_and_load_parser(self, data: dict) -> None:
        swagger_version: Optional[str] = data.get("swagger", None)  # OpenAPI version 2
        openapi_version: Optional[str] = data.get("openapi", None)  # OpenAPI version 3
        doc_config_version = swagger_version or openapi_version
        assert doc_config_version is not None, "PyMock-API cannot get the OpenAPI document version."
        assert isinstance(doc_config_version, str)
        set_openapi_version(doc_config_version)
        self.reload_schema_parser_factory()

    def to_api_config(self, base_url: str = "") -> APIConfig:  # type: ignore[override]
        api_config = APIConfig(name="", description="", apis=MockAPIs(base=BaseConfig(url=base_url), apis={}))
        assert api_config.apis is not None and api_config.apis.apis == {}
        for path, openapi_doc_api in self.paths.items():
            path = self._align_url_format(path)
            base_url = self._align_url_format(base_url)
            apis = openapi_doc_api.to_adapter_api(path=path)
            for api in apis:
                api_config.apis.apis[
                    self._generate_api_key(path=path, base_url=base_url, http_method=api.http_method)
                ] = api.to_api_config(base_url=base_url)
        return api_config

    def _align_url_format(self, path: str) -> str:
        return f"/{path}" if path and path[0] != "/" else path

    def _generate_api_key(self, path: str, base_url: str, http_method: str) -> str:
        return "_".join([http_method.lower(), path.replace(base_url, "")[1:].replace("/", "_")])
