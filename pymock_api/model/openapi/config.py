from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .. import APIConfig, MockAPIs
from ..api_config import BaseConfig
from ..enums import OpenAPIVersion
from ._base import (
    BaseOpenAPIDataModel,
    Transferable,
    get_openapi_version,
    set_openapi_version,
)
from ._tmp_data_model import TmpAPIConfig, set_component_definition


@dataclass
class Tag(BaseOpenAPIDataModel):
    name: str = field(default_factory=str)
    description: str = field(default_factory=str)

    @classmethod
    def generate(cls, detail: dict) -> "Tag":
        return Tag().deserialize(data=detail)

    def deserialize(self, data: Dict) -> "Tag":
        self.name = data["name"]
        self.description = data["description"]
        return self


@dataclass
class OpenAPIDocumentConfig(Transferable):
    paths: Dict[str, TmpAPIConfig] = field(default_factory=dict)
    tags: List[Tag] = field(default_factory=list)

    def deserialize(self, data: Dict) -> "OpenAPIDocumentConfig":
        self._chk_version_and_load_parser(data)

        if get_openapi_version() is OpenAPIVersion.V2:
            set_component_definition(data.get("definitions", {}))
        else:
            set_component_definition(data.get("components", {}))
        for path, config in data.get("paths", {}).items():
            self.paths[path] = TmpAPIConfig().deserialize(config)
        self.tags = list(map(lambda t: Tag.generate(t), data.get("tags", [])))

        return self

    def _chk_version_and_load_parser(self, data: dict) -> None:
        swagger_version: Optional[str] = data.get("swagger", None)  # OpenAPI version 2
        openapi_version: Optional[str] = data.get("openapi", None)  # OpenAPI version 3
        doc_config_version = swagger_version or openapi_version
        assert doc_config_version is not None, "PyMock-API cannot get the OpenAPI document version."
        assert isinstance(doc_config_version, str)
        set_openapi_version(doc_config_version)

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
