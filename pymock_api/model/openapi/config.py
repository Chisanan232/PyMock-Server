from dataclasses import dataclass, field
from typing import Dict, List, Optional, cast

from .. import APIConfig, MockAPI, MockAPIs
from ..api_config import BaseConfig

# from ..api_config.apis import APIParameter as PyMockAPIParameter
from ..enums import ResponseStrategy
from ._base import BaseOpenAPIDataModel, Transferable, set_openapi_version
from ._parser import APIParser, OpenAPIDocumentConfigParser
from ._tmp_data_model import (
    RequestParameter,
    ResponseProperty,
    set_component_definition,
)


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
class API(Transferable):
    path: str = field(default_factory=str)
    http_method: str = field(default_factory=str)
    parameters: List[RequestParameter] = field(default_factory=list)
    response: ResponseProperty = field(default_factory=ResponseProperty)
    tags: List[str] = field(default_factory=list)

    @classmethod
    def generate(cls, api_path: str, http_method: str, detail: dict) -> "API":
        api = API()
        api.path = api_path
        api.http_method = http_method
        api.deserialize(data=detail)
        return api

    def deserialize(self, data: Dict) -> "API":
        parser = APIParser(parser=self.schema_parser_factory.path(data=data))

        self.parameters = parser.process_api_parameters(http_method=self.http_method)
        self.response = parser.process_responses()
        self.tags = parser.process_tags()

        return self

    def to_api_config(self, base_url: str = "") -> MockAPI:  # type: ignore[override]
        mock_api = MockAPI(url=self.path.replace(base_url, ""), tag=self.tags[0] if self.tags else "")

        # Handle request config
        mock_api.set_request(
            method=self.http_method.upper(),
            parameters=list(map(lambda p: p.to_api_config(), self.parameters)),
        )

        # Handle response config
        print(f"[DEBUG in src] self.response: {self.response}")
        if list(filter(lambda p: p.name == "", self.response.data or [])):
            values = []
        else:
            values = self.response.data
        print(f"[DEBUG in to_api_config] values: {values}")
        resp_props_values = [p.to_pymock_api_config() for p in values] if values else values
        mock_api.set_response(strategy=ResponseStrategy.OBJECT, iterable_value=resp_props_values)  # type: ignore[arg-type]
        return mock_api


@dataclass
class OpenAPIDocumentConfig(Transferable):
    paths: List[API] = field(default_factory=list)
    tags: List[Tag] = field(default_factory=list)

    def deserialize(self, data: Dict) -> "OpenAPIDocumentConfig":
        self._chk_version_and_load_parser(data)

        openapi_schema_parser = self.schema_parser_factory.entire_config(data=data)
        set_component_definition(openapi_schema_parser)
        parser = OpenAPIDocumentConfigParser(parser=openapi_schema_parser)
        self.paths = cast(List[API], parser.process_paths(data_modal=API))
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
        for openapi_doc_api in self.paths:
            base_url = self._align_url_format(base_url, openapi_doc_api)
            api_config.apis.apis[self._generate_api_key(base_url, openapi_doc_api)] = openapi_doc_api.to_api_config(
                base_url=base_url
            )
        return api_config

    def _align_url_format(self, base_url: str, openapi_doc_api: API) -> str:
        if openapi_doc_api.path[0] != "/":
            openapi_doc_api.path = f"/{openapi_doc_api.path}"
        if base_url and base_url[0] != "/":
            base_url = f"/{base_url}"
        return base_url

    def _generate_api_key(self, base_url: str, openapi_doc_api: API) -> str:
        return "_".join([openapi_doc_api.http_method, openapi_doc_api.path.replace(base_url, "")[1:].replace("/", "_")])
