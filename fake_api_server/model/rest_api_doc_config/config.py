import logging
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type, Union, cast

try:
    from http import HTTPMethod, HTTPStatus
except ImportError:
    from http import HTTPStatus
    from fake_api_server.model.http import HTTPMethod  # type: ignore[assignment]

from fake_api_server.exceptions import CannotParsingAPIDocumentVersion
from fake_api_server.model.api_config import BaseConfig
from fake_api_server.model.api_config import FakeAPIConfig as PyFake_APIConfig
from fake_api_server.model.api_config import MockAPIs

from ._base import (
    BaseOpenAPIDataModel,
    Transferable,
    get_openapi_version,
    set_openapi_version,
)
from ._base_model_adapter import (
    BaseAPIAdapter,
    BaseRefPropertyDetailAdapter,
    BaseRequestParameterAdapter,
    BaseResponsePropertyAdapter,
)
from ._factory import _BaseAdapterFactory
from ._js_handlers import ApiDocValueFormat, ensure_type_is_python_type
from ._model_adapter import (
    APIAdapter,
    FormatAdapter,
    PropertyDetailAdapter,
    RequestParameterAdapter,
    ResponsePropertyAdapter,
)
from .base_config import (
    BaseAPIConfig,
    BaseAPIConfigWithMethodV2,
    BaseAPIConfigWithMethodV3,
    BaseAPIDocConfig,
    BaseHttpConfigV2,
    BaseHttpConfigV3,
    BaseReferenceConfig,
    BaseReferenceConfigProperty,
    BaseRequestSchema,
    _BaseAPIConfigWithMethod,
    _BaseRequestParameter,
    _Default_Required,
    set_component_definition,
)
from .content_type import ContentType
from .version import OpenAPIVersion

logger = logging.getLogger(__name__)


class AdapterFactory(_BaseAdapterFactory):
    def generate_value_format(self, **kwargs) -> FormatAdapter:
        return FormatAdapter(**kwargs)

    def generate_property_details(self, **kwargs) -> BaseRefPropertyDetailAdapter:
        return PropertyDetailAdapter(**kwargs)

    def generate_request_params(self, **kwargs) -> BaseRequestParameterAdapter:
        return RequestParameterAdapter(**kwargs)

    def generate_response_props(self, **kwargs) -> BaseResponsePropertyAdapter:
        return ResponsePropertyAdapter(**kwargs)

    def generate_api(self, **kwargs) -> BaseAPIAdapter:
        return APIAdapter(**kwargs)


@dataclass
class RequestSchema(BaseRequestSchema):
    title: Optional[str] = None
    value_type: Optional[str] = None
    default: Optional[Any] = None
    ref: Optional[str] = None

    _adapter_factory = AdapterFactory()

    def deserialize(self, data: dict) -> "RequestSchema":
        self.title = data.get("title", None)
        self.value_type = ensure_type_is_python_type(data["type"]) if data.get("type", None) else None
        self.default = data.get("default", None)
        self.ref = data.get("$ref", None)
        return self

    def has_ref(self) -> str:
        return "ref" if self.ref else ""

    def get_ref(self) -> str:
        assert self.ref
        return self.ref

    @property
    def _reference_object_type(self) -> Type["ReferenceConfig"]:
        return ReferenceConfig


@dataclass
class RequestParameter(_BaseRequestParameter):
    name: str = field(default_factory=str)
    query_in: Optional[str] = None
    required: bool = False
    value_type: Optional[str] = None
    format: Optional[ApiDocValueFormat] = None
    default: Optional[Any] = None
    items: Optional[List["RequestParameter"]] = None  # type: ignore[assignment]
    schema: Optional["RequestSchema"] = None  # type: ignore[assignment]

    _adapter_factory = AdapterFactory()

    def _convert_items(self) -> List[Union["RequestParameter"]]:
        assert self.items
        if True in list(map(lambda e: not isinstance(e, (dict, RequestParameter)), self.items)):
            raise ValueError(
                f"There are some invalid data type item in the property *items*. Current *items*: {self.items}"
            )
        return [RequestParameter().deserialize(i) if isinstance(i, dict) else i for i in (self.items or [])]

    def deserialize(self, data: dict) -> "RequestParameter":
        self.name = data.get("name", "")
        self.query_in = data.get("in", None)
        self.required = data.get("required", True)
        formatter = data.get("format", None)
        if formatter:
            self.format = ApiDocValueFormat.to_enum(formatter)
        self.enum = data.get("enum", None)

        items = data.get("items", [])
        if items:
            self.items = items if isinstance(items, list) else [items]
            self.items = self._convert_items()

        schema = data.get("schema", {})
        if schema:
            self.schema = RequestSchema().deserialize(schema)

        self.value_type = ensure_type_is_python_type(data.get("type", "")) or (
            self.schema.value_type if self.schema else ""
        )
        self.default = data.get("default", None) or (self.schema.default if self.schema else None)
        return self

    def has_ref(self) -> str:
        return "schema" if self.schema and self.schema.has_ref() else ""

    def get_ref(self) -> str:
        assert self.schema
        return self.schema.get_ref()

    def to_adapter(self) -> Optional["RequestParameterAdapter"]:
        if (self.query_in is None) or (self.query_in and self.query_in.lower() != "path"):
            items = []
            if self.items:
                for item in self.items:
                    adapter = item.to_adapter()
                    if adapter:
                        items.append(adapter)
            return RequestParameterAdapter(
                name=self.name,
                required=(self.required or False),
                value_type=self.value_type,
                default=self.default,
                format=FormatAdapter(
                    formatter=self.format,
                    enum=self.enum,
                ),
                items=items,
            )
        return None

    @property
    def _reference_object_type(self) -> Type["ReferenceConfig"]:
        return ReferenceConfig


@dataclass
class ReferenceConfigProperty(BaseReferenceConfigProperty):
    title: Optional[str] = None
    value_type: Optional[str] = None
    format: Optional[ApiDocValueFormat] = None  # For OpenAPI v3
    default: Optional[str] = None  # For OpenAPI v3 request part
    enums: List[str] = field(default_factory=list)
    ref: Optional[str] = None
    items: Optional["ReferenceConfigProperty"] = None
    additionalProperties: Optional["ReferenceConfigProperty"] = None

    _adapter_factory = AdapterFactory()

    @classmethod
    def deserialize(cls, data: Dict) -> "ReferenceConfigProperty":
        formatter = data.get("format", None)
        return ReferenceConfigProperty(
            title=data.get("title", None),
            value_type=ensure_type_is_python_type(data["type"]) if data.get("type", None) else None,
            format=ApiDocValueFormat.to_enum(formatter) if formatter else None,
            default=data.get("default", None),
            enums=data.get("enum", []),
            ref=data.get("$ref", None),
            items=ReferenceConfigProperty.deserialize(data["items"]) if data.get("items", None) else None,
            additionalProperties=(
                ReferenceConfigProperty.deserialize(data["additionalProperties"])
                if data.get("additionalProperties", None)
                else None
            ),
        )

    def has_ref(self) -> str:
        if self.ref:
            return "ref"
        # TODO: It should also integration *items* into this utility function
        # elif self.items and self.items.has_ref():
        #     return "items"
        elif self.additionalProperties and self.additionalProperties.has_ref():
            return "additionalProperties"
        else:
            return ""

    def get_ref(self) -> str:
        ref = self.has_ref()
        if ref == "additionalProperties":
            assert self.additionalProperties.ref  # type: ignore[union-attr]
            return self.additionalProperties.ref  # type: ignore[union-attr]
        return self.ref  # type: ignore[return-value]

    def is_empty(self) -> bool:
        return not (self.value_type or self.ref)

    def process_response_from_data(
        self,
        init_response: Optional["ResponsePropertyAdapter"] = None,  # type: ignore[override]
    ) -> "ResponsePropertyAdapter":
        if not init_response:
            init_response = ResponsePropertyAdapter.initial_response_data()
        response_config = self._generate_response(
            init_response=init_response,
            property_value=self,
        )
        response_data_prop = self._ensure_data_structure_when_object_strategy(init_response, response_config)
        init_response.data.append(response_data_prop)  # type: ignore[arg-type]
        return init_response

    @property
    def _reference_object_type(self) -> Type["ReferenceConfig"]:
        return ReferenceConfig


@dataclass
class ReferenceConfig(BaseReferenceConfig):
    title: Optional[str] = None
    value_type: str = field(default_factory=str)  # unused
    required: Optional[List[str]] = None
    properties: Dict[str, BaseReferenceConfigProperty] = field(default_factory=dict)

    _adapter_factory = AdapterFactory()

    @classmethod
    def deserialize(cls, data: Dict) -> "ReferenceConfig":
        properties = {}
        properties_config: dict = data.get("properties", {})
        if properties_config:
            for k, v in properties_config.items():
                properties[k] = ReferenceConfigProperty.deserialize(v)
        return ReferenceConfig(
            title=data.get("title", None),
            value_type=ensure_type_is_python_type(data["type"]) if data.get("type", None) else "",
            required=data.get("required", None),
            properties=properties,  # type: ignore[arg-type]
        )

    def process_reference_object(
        self,
        init_response: "ResponsePropertyAdapter",  # type: ignore[override]
        empty_body_key: str = "",
    ) -> "ResponsePropertyAdapter":
        response_schema_properties: Dict[str, BaseReferenceConfigProperty] = self.properties or {}
        if response_schema_properties:
            for k, v in response_schema_properties.items():
                # Check reference again
                if v.has_ref():
                    response_prop = v.get_schema_ref().process_reference_object(
                        init_response=ResponsePropertyAdapter.initial_response_data(),
                        empty_body_key=k,
                    )
                    # TODO: It should have better way to handle output streaming
                    if len(list(filter(lambda d: d.value_type == "file", response_prop.data))) != 0:
                        # It's file inputStream
                        response_config = response_prop.data[0]
                    else:
                        response_config = PropertyDetailAdapter(
                            name="",
                            required=_Default_Required.empty,
                            value_type="dict",
                            format=None,
                            items=response_prop.data,  # type: ignore[arg-type]
                        )
                else:
                    response_config = self._generate_response(  # type: ignore[assignment]
                        init_response=init_response,
                        property_value=v,
                    )
                response_data_prop = self._ensure_data_structure_when_object_strategy(init_response, response_config)
                response_data_prop.name = k
                response_data_prop.required = k in (self.required or [k])
                init_response.data.append(response_data_prop)  # type: ignore[arg-type]
        else:
            # The section which doesn't have setting body
            response_config = PropertyDetailAdapter.generate_empty_response()
            if self.title == "InputStream":
                response_config.value_type = "file"

                response_data_prop = self._ensure_data_structure_when_object_strategy(init_response, response_config)
                response_data_prop.name = empty_body_key
                response_data_prop.required = empty_body_key in (self.required or [empty_body_key])
                init_response.data.append(response_data_prop)  # type: ignore[arg-type]
            else:
                response_data_prop = self._ensure_data_structure_when_object_strategy(init_response, response_config)
                response_data_prop.name = "THIS_IS_EMPTY"
                response_data_prop.required = False
                init_response.data.append(response_data_prop)  # type: ignore[arg-type]
        return init_response


@dataclass
class HttpConfigV2(BaseHttpConfigV2):
    schema: Optional[BaseReferenceConfigProperty] = None

    _adapter_factory = AdapterFactory()

    @classmethod
    def deserialize(cls, data: dict) -> "HttpConfigV2":
        assert data is not None and isinstance(data, dict)
        return HttpConfigV2(
            schema=ReferenceConfigProperty.deserialize(data.get("schema", {})),
        )

    def has_ref(self) -> str:
        return "schema" if self.schema and self.schema.has_ref() else ""

    def get_ref(self) -> str:
        assert self.has_ref()
        assert self.schema.ref  # type: ignore[union-attr]
        return self.schema.ref  # type: ignore[union-attr]

    @property
    def _reference_object_type(self) -> Type["ReferenceConfig"]:
        return ReferenceConfig


@dataclass
class HttpConfigV3(BaseHttpConfigV3):
    content: Optional[Dict[ContentType, BaseHttpConfigV2]] = None

    _adapter_factory = AdapterFactory()

    @classmethod
    def deserialize(cls, data: dict) -> "HttpConfigV3":
        assert data is not None and isinstance(data, dict)
        content_config: Dict[ContentType, BaseHttpConfigV2] = {}
        for content_type, config in data.get("content", {}).items() or {}:
            content_config[ContentType.to_enum(content_type)] = HttpConfigV2.deserialize(config)
        return HttpConfigV3(content=content_config)

    def exist_setting(self, content_type: Union[str, ContentType]) -> Optional[ContentType]:
        content_type = ContentType.to_enum(content_type) if isinstance(content_type, str) else content_type
        if content_type in (self.content or {}).keys():
            return content_type
        else:
            return None

    def get_setting(self, content_type: Union[str, ContentType]) -> HttpConfigV2:
        content_type = self.exist_setting(content_type=content_type)  # type: ignore[assignment]
        if content_type is None:
            raise ValueError("Cannot find the mapping setting of content type.")
        assert self.content and len(self.content.values()) > 0
        return self.content[content_type]  # type: ignore[index, return-value]


@dataclass
class APIConfigWithMethodV2(BaseAPIConfigWithMethodV2):
    produces: List[str] = field(default_factory=list)
    responses: Dict[HTTPStatus, BaseHttpConfigV2] = field(default_factory=dict)

    _adapter_factory = AdapterFactory()

    @classmethod
    def deserialize(cls, data: dict) -> "APIConfigWithMethodV2":
        deserialized_data = cast(APIConfigWithMethodV2, super().deserialize(data))
        deserialized_data.produces = data.get("produces", [])
        return deserialized_data

    @staticmethod
    def _deserialize_request(data: dict) -> RequestParameter:
        return RequestParameter().deserialize(data)

    @staticmethod
    def _deserialize_response(data: dict) -> BaseHttpConfigV2:
        return HttpConfigV2.deserialize(data)

    def to_request_adapter(self, http_method: str) -> List["RequestParameterAdapter"]:  # type: ignore[override]
        return self._initial_request_parameters_model(self.parameters, self.parameters)  # type: ignore[arg-type, return-value]

    def _deserialize_empty_reference_config_properties(self) -> BaseReferenceConfigProperty:
        return ReferenceConfigProperty.deserialize({})

    def _get_http_config(self, status_200_response: BaseAPIDocConfig) -> BaseHttpConfigV2:
        assert isinstance(status_200_response, BaseHttpConfigV2)
        return status_200_response


@dataclass
class APIConfigWithMethodV3(BaseAPIConfigWithMethodV3):
    request_body: Optional[BaseHttpConfigV3] = None
    responses: Dict[HTTPStatus, BaseHttpConfigV3] = field(default_factory=dict)

    _adapter_factory = AdapterFactory()

    @classmethod
    def deserialize(cls, data: dict) -> "APIConfigWithMethodV3":
        deserialized_data = cast(APIConfigWithMethodV3, super().deserialize(data))
        deserialized_data.request_body = (
            HttpConfigV3().deserialize(data["requestBody"]) if data.get("requestBody", {}) else None
        )
        return deserialized_data

    @staticmethod
    def _deserialize_request(data: dict) -> RequestParameter:
        return RequestParameter().deserialize(data)

    @staticmethod
    def _deserialize_response(data: dict) -> HttpConfigV3:
        return HttpConfigV3.deserialize(data)

    def to_request_adapter(self, http_method: str) -> List["RequestParameterAdapter"]:  # type: ignore[override]
        _data: List[Union[_BaseRequestParameter, BaseHttpConfigV2]] = []
        no_ref_data: List[_BaseRequestParameter] = []
        if http_method.upper() == "GET":
            _data = no_ref_data = self.parameters  # type: ignore[assignment]
        else:
            if self.request_body:
                req_body_content_type: List[ContentType] = list(
                    filter(lambda ct: self.request_body.exist_setting(content_type=ct) is not None, ContentType)  # type: ignore[arg-type]
                )
                req_body_config = self.request_body.get_setting(content_type=req_body_content_type[0])
                _data = [req_body_config]
                no_ref_data = self.parameters
            else:
                _data = no_ref_data = self.parameters  # type: ignore[assignment]
        return self._initial_request_parameters_model(_data, no_ref_data)  # type: ignore[return-value]

    def _deserialize_empty_reference_config_properties(self) -> BaseReferenceConfigProperty:
        return ReferenceConfigProperty.deserialize({})

    def _get_http_config(self, status_200_response: BaseAPIDocConfig) -> BaseHttpConfigV2:
        # NOTE: This parsing way for OpenAPI (OpenAPI version 3)
        assert isinstance(status_200_response, BaseHttpConfigV3)
        status_200_response_model = status_200_response
        resp_value_format: List[ContentType] = list(
            filter(lambda ct: status_200_response_model.exist_setting(content_type=ct) is not None, ContentType)
        )
        return status_200_response_model.get_setting(content_type=resp_value_format[0])


@dataclass
class APIConfig(BaseAPIConfig):
    api: Dict[HTTPMethod, _BaseAPIConfigWithMethod] = field(default_factory=dict)

    _adapter_factory = AdapterFactory()

    def __len__(self):
        return len(self.api.keys())

    def deserialize(self, data: dict) -> "APIConfig":
        initial_api_config: _BaseAPIConfigWithMethod
        if get_openapi_version() is OpenAPIVersion.V2:
            initial_api_config = APIConfigWithMethodV2()
        else:
            initial_api_config = APIConfigWithMethodV3()

        for http_method, config in data.items():
            self.api[HTTPMethod(http_method.upper())] = initial_api_config.deserialize(config)

        return self

    def to_adapter(self, path: str) -> List[APIAdapter]:  # type: ignore[override]
        apis: List[APIAdapter] = []
        for http_method, http_config in self.api.items():
            api = APIAdapter.generate(api_path=path, http_method=http_method.name, detail=http_config)
            apis.append(api)
        return apis


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
class BaseAPIDocumentConfig(Transferable):
    paths: Dict[str, APIConfig] = field(default_factory=dict)
    tags: List[Tag] = field(default_factory=list)

    def deserialize(self, data: Dict) -> "BaseAPIDocumentConfig":
        self._parse_and_set_api_doc_version(data)

        for path, config in data.get("paths", {}).items():
            self.paths[path] = APIConfig().deserialize(config)
        self.tags = list(map(lambda t: Tag.generate(t), data.get("tags", [])))
        self._set_common_objects(data)

        return self

    def _parse_and_set_api_doc_version(self, data: dict) -> None:
        # Parse version info
        doc_config_version = self._parse_api_doc_version(data)
        # Set version info
        assert doc_config_version and isinstance(
            doc_config_version, str
        ), "PyFake-API-Server cannot get the OpenAPI document version."
        set_openapi_version(doc_config_version)

    @abstractmethod
    def _parse_api_doc_version(self, data: dict) -> str:
        pass

    @abstractmethod
    def _set_common_objects(self, data: Dict) -> None:
        pass

    def to_api_config(self, base_url: str = "") -> PyFake_APIConfig:  # type: ignore[override]
        api_config = PyFake_APIConfig(name="", description="", apis=MockAPIs(base=BaseConfig(url=base_url), apis={}))
        assert api_config.apis is not None and api_config.apis.apis == {}
        for path, openapi_doc_api in self.paths.items():
            path = self._align_url_format(path)
            base_url = self._align_url_format(base_url)
            apis = openapi_doc_api.to_adapter(path=path)
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
class SwaggerAPIDocumentConfig(BaseAPIDocumentConfig):
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
class OpenAPIDocumentConfig(BaseAPIDocumentConfig):
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
        raise CannotParsingAPIDocumentVersion()
