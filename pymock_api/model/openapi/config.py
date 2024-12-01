from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List

from .. import APIConfig, MockAPIs
from ..api_config import BaseConfig
from ..enums import OpenAPIVersion
from ._base import BaseOpenAPIDataModel, Transferable, set_openapi_version
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
class BaseOpenAPIDocumentConfig(Transferable):
    paths: Dict[str, TmpAPIConfig] = field(default_factory=dict)
    tags: List[Tag] = field(default_factory=list)

    def deserialize(self, data: Dict) -> "BaseOpenAPIDocumentConfig":
        self._parse_and_set_api_doc_version(data)

        for path, config in data.get("paths", {}).items():
            self.paths[path] = TmpAPIConfig().deserialize(config)
        self.tags = list(map(lambda t: Tag.generate(t), data.get("tags", [])))
        self._set_common_objects(data)

        return self

    def _parse_and_set_api_doc_version(self, data: dict) -> None:
        # Parse version info
        doc_config_version = self._parse_api_doc_version(data)
        # Set version info
        assert doc_config_version and isinstance(
            doc_config_version, str
        ), "PyMock-API cannot get the OpenAPI document version."
        set_openapi_version(doc_config_version)

    @abstractmethod
    def _parse_api_doc_version(self, data: dict) -> str:
        pass

    @abstractmethod
    def _set_common_objects(self, data: Dict) -> None:
        pass

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


@dataclass
class SwaggerAPIDocumentConfig(BaseOpenAPIDocumentConfig):
    """
    Swagger API documentation configuration (version 2).
    """

    _definitions: Dict[str, Dict] = field(default_factory=dict)

    @property
    def definitions(self) -> Dict[str, Dict]:
        return self._definitions

    @definitions.setter
    def definitions(self, d: Dict[str, Dict]) -> None:
        set_component_definition(d)
        self._definitions = d

    def _parse_api_doc_version(self, data: dict) -> str:
        return data["swagger"]  # OpenAPI version 2

    def _set_common_objects(self, data: Dict) -> None:
        self.definitions = data["definitions"]


@dataclass
class OpenAPIDocumentConfig(BaseOpenAPIDocumentConfig):
    """
    Open API documentation configuration (version 3).
    """

    _components: Dict[str, Dict] = field(default_factory=dict)

    @property
    def components(self) -> Dict[str, Dict]:
        return self._components

    @components.setter
    def components(self, d: Dict[str, Dict]) -> None:
        set_component_definition(d)
        self._components = d

    def _parse_api_doc_version(self, data: dict) -> str:
        return data["openapi"]  # OpenAPI version 3

    def _set_common_objects(self, data: Dict) -> None:
        self.components = data["components"]


def get_api_doc_version(data: Dict) -> OpenAPIVersion:
    if "swagger" in data.keys():
        return OpenAPIVersion.V2
    elif "openapi" in data.keys():
        return OpenAPIVersion.V3
    else:
        raise
