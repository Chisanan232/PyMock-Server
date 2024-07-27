from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, cast

from .. import APIConfig, MockAPI, MockAPIs
from ..api_config import BaseConfig, IteratorItem
from ..api_config.apis import APIParameter as PyMockAPIParameter
from ..enums import OpenAPIVersion, ResponseStrategy
from ._base import (
    BaseOpenAPIDataModel,
    Transferable,
    get_openapi_version,
    set_openapi_version,
)
from ._parser import APIParameterParser, APIParser, OpenAPIDocumentConfigParser
from ._schema_parser import _ReferenceObjectParser, set_component_definition
from ._tmp_data_model import TmpAPIParameterModel, TmpItemModel


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
class BaseProperty(BaseOpenAPIDataModel, ABC):
    name: str = field(default_factory=str)
    required: bool = False
    value_type: str = field(default_factory=str)
    default: Any = None
    items: Optional[List[Union[TmpAPIParameterModel, TmpItemModel]]] = None


@dataclass
class APIParameter(BaseProperty, Transferable):

    @classmethod
    def generate(cls, detail: Union[dict, TmpAPIParameterModel]) -> "APIParameter":
        return APIParameter().deserialize(data=detail)

    def deserialize(self, data: Union[Dict, TmpAPIParameterModel]) -> "APIParameter":
        if isinstance(data, dict):
            parser = APIParameterParser(self.schema_parser_factory.request_parameters(data))
            handled_data = parser.process_parameter(data)
        else:
            handled_data = data
        self.name = handled_data.name
        self.required = handled_data.required
        self.value_type = handled_data.value_type
        self.default = handled_data.default
        items = handled_data.items
        if items is not None:
            self.items = items if isinstance(items, list) else [items]  # type: ignore[list-item]
        return self

    def to_api_config(self) -> PyMockAPIParameter:  # type: ignore[override]

        def to_items(item_data: Union[TmpAPIParameterModel, TmpItemModel]) -> IteratorItem:
            if isinstance(item_data, TmpAPIParameterModel):
                return IteratorItem(
                    name=item_data.name,
                    required=item_data.required,
                    value_type=item_data.value_type,
                    items=[to_items(i) for i in (item_data.items or [])],
                )
            elif isinstance(item_data, TmpItemModel):
                return IteratorItem(
                    name="",
                    required=True,
                    value_type=item_data.value_type,
                    items=[],
                )
            else:
                raise TypeError(
                    f"The data model must be *TmpAPIParameterModel* or *TmpItemModel*. But it get *{item_data}*. Please check it."
                )

        return PyMockAPIParameter(
            name=self.name,
            required=self.required,
            value_type=self.value_type,
            default=self.default,
            value_format=None,
            items=[to_items(i) for i in (self.items or [])],
        )


@dataclass
class API(Transferable):
    path: str = field(default_factory=str)
    http_method: str = field(default_factory=str)
    parameters: List[APIParameter] = field(default_factory=list)
    response: Dict = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    process_response_strategy: ResponseStrategy = ResponseStrategy.OBJECT

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

        self.parameters = [
            APIParameter.generate(pd) for pd in self.process_api_parameters(parser, http_method=self.http_method)
        ]
        self.response = parser.process_responses(strategy=self.process_response_strategy)
        self.tags = parser.process_tags()

        return self

    def process_api_parameters(self, parser: APIParser, http_method: str) -> List[TmpAPIParameterModel]:

        def _deserialize_as_tmp_model(_data: dict) -> TmpAPIParameterModel:
            return APIParameterParser(self.schema_parser_factory.request_parameters(_data)).process_parameter(_data)

        def _initial_request_parameters_model(
            _data: List[dict], not_ref_data: List[dict]
        ) -> List[TmpAPIParameterModel]:
            has_ref_in_schema_param = list(filter(lambda p: _ReferenceObjectParser.has_ref(p) != "", _data))
            if has_ref_in_schema_param:
                # TODO: Ensure the value maps this condition is really only one
                handled_parameters = []
                for d in _data:
                    handled_parameters.extend(self._process_has_ref_parameters(d))
            else:
                # TODO: Parsing the data type of key *items* should be valid type of Python realm
                handled_parameters = [_deserialize_as_tmp_model(p) for p in not_ref_data]
            return handled_parameters

        if get_openapi_version() is OpenAPIVersion.V2:
            v2_params_data: List[dict] = parser.parser.get_request_parameters()
            return _initial_request_parameters_model(v2_params_data, v2_params_data)
        else:
            if http_method.upper() == "GET":
                get_method_params_data: List[dict] = parser.parser.get_request_parameters()
                return _initial_request_parameters_model(get_method_params_data, get_method_params_data)
            else:
                params_in_path_data: List[dict] = parser.parser.get_request_parameters()
                params_data: dict = parser.parser.get_request_body()
                return _initial_request_parameters_model([params_data], params_in_path_data)

    def _process_has_ref_parameters(self, data: Dict) -> List[TmpAPIParameterModel]:
        request_body_params = _ReferenceObjectParser.get_schema_ref(data)
        # TODO: Should use the reference to get the details of parameters.
        parameters: List[TmpAPIParameterModel] = []
        parser = self.schema_parser_factory.object(request_body_params)
        for param_name, param_props in parser.get_properties().items():
            props_parser = self.schema_parser_factory.request_parameters(param_props)
            items: Optional[dict] = props_parser.get_items()
            items_props = []
            if items:
                if _ReferenceObjectParser.has_ref(items):
                    # Sample data:
                    # {
                    #     'type': 'object',
                    #     'required': ['values', 'id'],
                    #     'properties': {
                    #         'values': {'type': 'number', 'example': 23434, 'description': 'value'},
                    #         'id': {'type': 'integer', 'format': 'int64', 'example': 1, 'description': 'ID'}
                    #     },
                    #     'title': 'UpdateOneFooDto'
                    # }
                    item = self._process_has_ref_parameters(data=items)
                    items_props.extend(item)
                else:
                    props_items_parser = self.schema_parser_factory.request_parameter_items(items)
                    item_type = props_items_parser.get_items_type()
                    assert item_type
                    items_props.append(
                        TmpAPIParameterModel(
                            name="",
                            required=True,
                            # "type": convert_js_type(items["type"]),
                            value_type=item_type,
                            default=items.get("default", None),
                            items=[],
                        ),
                    )

            parameters.append(
                TmpAPIParameterModel(
                    name=param_name,
                    required=param_name in parser.get_required(),
                    value_type=param_props["type"],
                    default=param_props.get("default", None),
                    items=items_props if items is not None else items,  # type: ignore[arg-type]
                ),
            )
        print(f"[DEBUG in APIParser._process_has_ref_parameters] parameters: {parameters}")
        return parameters

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
