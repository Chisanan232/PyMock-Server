from typing import Any, Dict, List, Optional, cast

from .. import APIConfig, MockAPI, MockAPIs
from ..api_config import BaseConfig
from ..api_config.apis import APIParameter as PyMockAPIParameter
from ..enums import ResponseStrategy
from ._base import (
    BaseOpenAPIDataModel,
    Transferable,
    set_component_definition,
    set_openapi_version,
)
from ._js_handlers import convert_js_type
from ._parser import APIParameterParser, APIParser, OpenAPIDocumentConfigParser


class Tag(BaseOpenAPIDataModel):
    def __init__(self):
        super().__init__()
        self.name: str = ""
        self.description: str = ""

    @classmethod
    def generate(cls, detail: dict) -> "Tag":
        return Tag().deserialize(data=detail)

    def deserialize(self, data: Dict) -> "Tag":
        parser = self.schema_parser_factory.tag(data)
        self.name = parser.get_name()
        self.description = parser.get_description()
        return self


class APIParameter(Transferable):
    def __init__(self):
        super().__init__()
        self.name: str = ""
        self.required: bool = False
        self.value_type: str = ""
        self.default: Any = None
        self.items: Optional[list] = None

    @classmethod
    def generate(cls, detail: dict) -> "APIParameter":
        return APIParameter().deserialize(data=detail)

    def deserialize(self, data: Dict) -> "APIParameter":
        parser = APIParameterParser(self.schema_parser_factory.request_parameters(data))
        handled_data = parser.process_parameter(data)
        self.name = handled_data.name  # type: ignore[attr-defined]
        self.required = handled_data.required  # type: ignore[attr-defined]
        self.value_type = convert_js_type(handled_data.type)  # type: ignore[attr-defined]
        self.default = handled_data.default  # type: ignore[attr-defined]
        items = handled_data.items  # type: ignore[attr-defined]
        if items is not None:
            self.items = items if isinstance(items, list) else [items]
        return self

    def to_api_config(self) -> PyMockAPIParameter:  # type: ignore[override]
        return PyMockAPIParameter(
            name=self.name,
            required=self.required,
            value_type=self.value_type,
            default=self.default,
            value_format=None,
            items=self.items,
        )


class API(Transferable):
    def __init__(self):
        super().__init__()
        self.path: str = ""
        self.http_method: str = ""
        self.parameters: List[APIParameter] = []
        self.response: Dict = {}
        self.tags: List[str] = []

        self.process_response_strategy: ResponseStrategy = ResponseStrategy.OBJECT

    @classmethod
    def generate(cls, api_path: str, http_method: str, detail: dict) -> "API":
        api = API()
        api.path = api_path
        api.http_method = http_method
        api.deserialize(data=detail)
        return api

    def deserialize(self, data: Dict) -> "API":
        # FIXME: Does it have better way to set the HTTP response strategy?
        if not self.process_response_strategy:
            raise ValueError("Please set the strategy how it should process HTTP response.")
        parser = APIParser(parser=self.schema_parser_factory.path(data=data))

        self.parameters = cast(
            List[APIParameter], parser.process_api_parameters(data_modal=APIParameter, http_method=self.http_method)
        )
        self.response = parser.process_responses(strategy=self.process_response_strategy)
        self.tags = parser.process_tags()

        return self

    def to_api_config(self, base_url: str = "") -> MockAPI:  # type: ignore[override]
        mock_api = MockAPI(url=self.path.replace(base_url, ""), tag=self.tags[0] if self.tags else "")
        mock_api.set_request(
            method=self.http_method.upper(),
            parameters=list(map(lambda p: p.to_api_config(), self.parameters)),
        )
        resp_strategy = self.response["strategy"]
        if resp_strategy is ResponseStrategy.OBJECT:
            if list(filter(lambda p: p["name"] == "", self.response["data"])):
                values = []
            else:
                values = self.response["data"]
            print(f"[DEBUG in to_api_config] values: {values}")
            mock_api.set_response(strategy=resp_strategy, iterable_value=values)
        else:
            mock_api.set_response(strategy=resp_strategy, value=self.response["data"])
        return mock_api


class OpenAPIDocumentConfig(Transferable):
    def __init__(self):
        super().__init__()
        self.paths: List[API] = []
        self.tags: List[Tag] = []

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
