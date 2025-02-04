import copy
import logging
import re
from abc import ABC, ABCMeta, abstractmethod
from collections import namedtuple
from dataclasses import dataclass, field
from pydoc import locate
from typing import Any, Callable, Dict, List, Optional, Type, Union

from ._js_handlers import ApiDocValueFormat

try:
    from http import HTTPMethod, HTTPStatus
except ImportError:
    from http import HTTPStatus
    from fake_api_server.model.http import HTTPMethod  # type: ignore[assignment]

from ._base_model_adapter import (
    BaseAPIAdapter,
    BaseRefPropertyDetailAdapter,
    BaseRequestParameterAdapter,
    BaseResponsePropertyAdapter,
)
from ._factory import _BaseAdapterFactory
from .content_type import ContentType

logger = logging.getLogger(__name__)

ComponentDefinition: Dict[str, dict] = {}


def get_component_definition() -> Dict:
    global ComponentDefinition
    return ComponentDefinition


def set_component_definition(openapi_common_objects: Dict) -> None:
    global ComponentDefinition
    ComponentDefinition = openapi_common_objects


_PropertyDefaultRequired = namedtuple("_PropertyDefaultRequired", ("empty", "general"))
_Default_Required: _PropertyDefaultRequired = _PropertyDefaultRequired(empty=False, general=True)


@dataclass
class BaseAPIDocConfig(metaclass=ABCMeta):
    _adapter_factory: _BaseAdapterFactory = field(repr=False, init=False)

    def _ensure_data_structure_when_object_strategy(
        self,
        init_response: BaseResponsePropertyAdapter,
        response_data_prop: Union[BaseRefPropertyDetailAdapter, List[BaseRefPropertyDetailAdapter]],
    ) -> BaseRefPropertyDetailAdapter:
        assert isinstance(response_data_prop, BaseRefPropertyDetailAdapter)
        assert isinstance(
            init_response.data, list
        ), "The response data type must be *list* if its HTTP response strategy is object."
        assert (
            len(list(filter(lambda d: not isinstance(d, BaseRefPropertyDetailAdapter), init_response.data))) == 0
        ), "Each column detail must be *dict* if its HTTP response strategy is object."
        return response_data_prop

    def _generate_response(
        self,
        init_response: BaseResponsePropertyAdapter,
        property_value: "BaseReferenceConfigProperty",
    ) -> Union[BaseRefPropertyDetailAdapter, List[BaseRefPropertyDetailAdapter]]:
        if property_value.is_empty():
            return self._adapter_factory.generate_property_details().generate_empty_response()
        if property_value.has_ref():
            resp_prop_data = property_value.get_schema_ref()
        else:
            resp_prop_data = property_value  # type: ignore[assignment]
        assert resp_prop_data
        return self._generate_response_from_data(
            init_response=init_response,
            resp_prop_data=resp_prop_data,
        )

    def _generate_response_from_data(
        self,
        init_response: BaseResponsePropertyAdapter,
        resp_prop_data: Union["BaseReferenceConfigProperty", "BaseReferenceConfig"],
    ) -> Union[BaseRefPropertyDetailAdapter, List[BaseRefPropertyDetailAdapter]]:

        def _handle_list_type_data(
            data: BaseReferenceConfigProperty,
            noref_val_process_callback: Callable,
            ref_val_process_callback: Callable,
            response: BaseRefPropertyDetailAdapter = self._adapter_factory.generate_property_details(),
        ) -> BaseRefPropertyDetailAdapter:
            items_data = data.items
            assert items_data
            if items_data.has_ref():
                response = _handle_reference_object(
                    response, items_data, noref_val_process_callback, ref_val_process_callback
                )
            else:
                response_item_value = self._generate_response_from_data(
                    init_response=init_response,
                    resp_prop_data=items_data,
                )
                items = None
                if response_item_value:
                    items = response_item_value if isinstance(response_item_value, list) else [response_item_value]
                response = self._adapter_factory.generate_property_details(
                    name="",
                    required=_Default_Required.general,
                    value_type="list",
                    items=items,
                )
            return response

        def _handle_reference_object(
            response: BaseRefPropertyDetailAdapter,
            items_data: BaseReferenceConfigProperty,
            noref_val_process_callback: Callable[
                # item_k, item_v, response
                [str, BaseReferenceConfigProperty, BaseRefPropertyDetailAdapter],
                BaseRefPropertyDetailAdapter,
            ],
            ref_val_process_callback: Callable[
                [
                    # item_k, item_v, response, single_response, noref_val_process_callback
                    str,
                    BaseReferenceConfigProperty,
                    BaseRefPropertyDetailAdapter,
                    BaseReferenceConfig,
                    Callable[
                        [str, BaseReferenceConfigProperty, BaseRefPropertyDetailAdapter],
                        BaseRefPropertyDetailAdapter,
                    ],
                ],
                BaseRefPropertyDetailAdapter,
            ],
        ) -> BaseRefPropertyDetailAdapter:
            single_response: Optional[BaseReferenceConfig] = items_data.get_schema_ref()
            assert single_response
            for item_k, item_v in (single_response.properties or {}).items():
                if item_v.has_ref():
                    response = ref_val_process_callback(
                        item_k, item_v, response, single_response, noref_val_process_callback
                    )
                else:
                    response = noref_val_process_callback(item_k, item_v, response)
            return response

        def _handle_list_type_value_with_object_strategy(
            data: BaseReferenceConfigProperty,
        ) -> BaseRefPropertyDetailAdapter:

            def _ref_process_callback(
                item_k: str,
                item_v: BaseReferenceConfigProperty,
                response: BaseRefPropertyDetailAdapter,
                ref_single_response: BaseReferenceConfig,
                noref_val_process_callback: Callable[
                    [str, BaseReferenceConfigProperty, BaseRefPropertyDetailAdapter],
                    BaseRefPropertyDetailAdapter,
                ],
            ) -> BaseRefPropertyDetailAdapter:
                assert ref_single_response.required
                item_k_data_prop = self._adapter_factory.generate_property_details(
                    name=item_k,
                    required=item_k in ref_single_response.required,
                    value_type=item_v.value_type or "dict",
                    format=self._adapter_factory.generate_value_format(
                        formatter=item_v.format,
                        enum=item_v.enums,
                    ),
                    items=[],
                )
                ref_item_v_response = _handle_reference_object(
                    items_data=item_v,
                    noref_val_process_callback=noref_val_process_callback,
                    ref_val_process_callback=_ref_process_callback,
                    response=item_k_data_prop,
                )
                if response.items:
                    assert response.items and isinstance(response.items, list)
                    response.items.append(ref_item_v_response)
                else:
                    response.items = (
                        [ref_item_v_response] if not isinstance(ref_item_v_response, list) else ref_item_v_response
                    )
                return response

            def _noref_process_callback(
                item_k: str,
                item_v: BaseReferenceConfigProperty,
                response_data_prop: BaseRefPropertyDetailAdapter,
            ) -> BaseRefPropertyDetailAdapter:
                item_type = item_v.value_type
                item = self._adapter_factory.generate_property_details(
                    name=item_k,
                    required=_Default_Required.general,
                    value_type=item_type,
                    format=self._adapter_factory.generate_value_format(
                        formatter=item_v.format,
                        enum=item_v.enums,
                    ),
                )
                assert isinstance(response_data_prop.items, list), "The data type of property *items* must be *list*."
                response_data_prop.items.append(item)
                return response_data_prop

            response_data_prop = self._adapter_factory.generate_property_details(
                name="",
                required=_Default_Required.general,
                value_type=data.value_type,
                # TODO: Set the *format* property correctly
                format=None,
                items=[],
            )
            response_data_prop = _handle_list_type_data(
                data=data,
                noref_val_process_callback=_noref_process_callback,
                ref_val_process_callback=_ref_process_callback,
                response=response_data_prop,
            )
            return response_data_prop

        def _handle_object_type_value_with_object_strategy(
            data: Union[BaseReferenceConfigProperty, BaseReferenceConfig],
        ) -> Union[BaseRefPropertyDetailAdapter, List[BaseRefPropertyDetailAdapter]]:
            data_title = data.title
            if data_title:
                # Example data: {'type': 'object', 'title': 'InputStream'}
                if re.search(data_title, "InputStream", re.IGNORECASE):
                    return self._adapter_factory.generate_property_details(
                        name="",
                        required=_Default_Required.general,
                        value_type="file",
                        # TODO: Set the *format* property correctly
                        format=None,
                        items=None,
                    )

            # Check reference first
            assert not isinstance(data, BaseReferenceConfig)
            has_ref = data.has_ref()
            if has_ref:
                # Process reference
                resp = data.process_response_from_reference(
                    init_response=init_response,
                )
                if has_ref == "additionalProperties":
                    return self._adapter_factory.generate_property_details(
                        name="additionalKey",
                        required=_Default_Required.general,
                        value_type="dict",
                        items=resp.data,
                    )
                return resp.data
            else:
                # Handle the schema *additionalProperties*
                assert isinstance(data, BaseReferenceConfigProperty)
                additional_properties = data.additionalProperties
                assert additional_properties
                additional_properties_type = additional_properties.value_type
                assert additional_properties_type
                if locate(additional_properties_type) in [list, dict, "file"]:
                    items_config_data = _handle_list_type_value_with_object_strategy(additional_properties)
                    # Collection type config has been wrap one level of *additionalKey*. So it doesn't need to wrap
                    # it again.
                    return items_config_data
                else:
                    return self._adapter_factory.generate_property_details(
                        name="",
                        required=_Default_Required.general,
                        value_type="dict",
                        items=[
                            self._adapter_factory.generate_property_details(
                                name="additionalKey",
                                required=_Default_Required.general,
                                value_type=additional_properties_type,
                                format=self._adapter_factory.generate_value_format(
                                    formatter=additional_properties.format,
                                    enum=additional_properties.enums,
                                ),
                                items=None,
                            ),
                        ],
                    )

        def _handle_other_types_value_with_object_strategy(
            data: Union[BaseReferenceConfigProperty, BaseReferenceConfig],
        ) -> BaseRefPropertyDetailAdapter:
            return self._adapter_factory.generate_property_details(
                name="",
                required=_Default_Required.general,
                value_type=data.value_type,
                format=(
                    self._adapter_factory.generate_value_format(
                        formatter=data.format,
                        enum=data.enums,
                    )
                    if isinstance(data, BaseReferenceConfigProperty)
                    else None
                ),
                items=None,
            )

        def _handle_each_data_types_response_with_object_strategy(
            data: Union[BaseReferenceConfigProperty, BaseReferenceConfig],
        ) -> Union[BaseRefPropertyDetailAdapter, List[BaseRefPropertyDetailAdapter]]:
            if locate(data.value_type) == list:  # type: ignore[arg-type]
                assert isinstance(data, BaseReferenceConfigProperty)
                return _handle_list_type_value_with_object_strategy(data)
            elif locate(data.value_type) == dict:  # type: ignore[arg-type]
                return _handle_object_type_value_with_object_strategy(data)
            else:
                return _handle_other_types_value_with_object_strategy(data)

        if not resp_prop_data.value_type:
            assert not isinstance(resp_prop_data, BaseReferenceConfig)
            assert resp_prop_data.has_ref()
            resp_prop_data.value_type = "dict"
            return _handle_each_data_types_response_with_object_strategy(resp_prop_data)
        return _handle_each_data_types_response_with_object_strategy(resp_prop_data)


@dataclass
class BaseReferencialConfig(BaseAPIDocConfig):

    @abstractmethod
    def has_ref(self) -> str:
        pass

    @abstractmethod
    def get_ref(self) -> str:
        pass

    def get_schema_ref(self) -> "BaseReferenceConfig":
        def _get_schema(component_def_data: dict, paths: List[str], i: int) -> dict:
            if i == len(paths) - 1:
                return component_def_data[paths[i]]
            else:
                return _get_schema(component_def_data[paths[i]], paths, i + 1)

        _has_ref = self.has_ref()
        if not _has_ref:
            raise ValueError("This parameter has no ref in schema.")
        schema_path = self.get_ref().replace("#/", "").split("/")[1:]
        # Operate the component definition object
        return self._reference_object_type.deserialize(_get_schema(get_component_definition(), schema_path, 0))

    @property
    @abstractmethod
    def _reference_object_type(self) -> Type["BaseReferenceConfig"]:
        pass

    def process_has_ref_request_parameters(self) -> List[BaseRequestParameterAdapter]:
        request_body_params = self.get_schema_ref()
        parameters: List[BaseRequestParameterAdapter] = []
        for param_name, param_props in request_body_params.properties.items():
            items: Optional[BaseReferenceConfigProperty] = param_props.items
            items_props = []
            if items:
                if items.has_ref():
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
                    item = items.process_has_ref_request_parameters()
                    items_props.extend(item)
                else:
                    assert items.value_type
                    items_props.append(
                        self._adapter_factory.generate_request_params().deserialize_by_prps(
                            name="",
                            required=True,
                            value_type=items.value_type,
                            formatter=None if items.value_type in ["dict", "list"] else items.format,
                            enum=items.enums,
                            default=items.default,
                            items=[],
                        ),
                    )

            parameters.append(
                self._adapter_factory.generate_request_params().deserialize_by_prps(
                    name=param_name,
                    required=param_name in (request_body_params.required or []),
                    value_type=param_props.value_type or "",
                    formatter=param_props.format,
                    enum=param_props.enums,
                    default=param_props.default,
                    items=items_props if items is not None else items,  # type: ignore[arg-type]
                ),
            )
        return parameters

    def process_response_from_reference(
        self,
        init_response: Optional[BaseResponsePropertyAdapter] = None,
    ) -> BaseResponsePropertyAdapter:
        if not init_response:
            init_response = self._adapter_factory.generate_response_props().initial_response_data()  # type: ignore[assignment]
        response = self.get_schema_ref().process_reference_object(init_response=init_response)  # type: ignore[arg-type]

        # Handle the collection data which has empty body
        new_response = copy.copy(response)
        response_columns_setting = response.data or []
        new_response.data = self._process_empty_body_response(response_columns_setting=response_columns_setting)
        response = new_response

        return response

    def _process_empty_body_response(
        self, response_columns_setting: List[BaseRefPropertyDetailAdapter]
    ) -> List[BaseRefPropertyDetailAdapter]:
        new_response_columns_setting = []
        for resp_column in response_columns_setting:
            # element self
            if resp_column.name == "THIS_IS_EMPTY":
                resp_column.name = ""
                resp_column.is_empty = True
            else:
                # element's property *items*
                response_data_prop_items = resp_column.items or []
                if response_data_prop_items and len(response_data_prop_items) != 0:
                    if response_data_prop_items[0].name == "THIS_IS_EMPTY":
                        resp_column.is_empty = True
                        resp_column.items = []
                    else:
                        resp_column.items = self._process_empty_body_response(
                            response_columns_setting=response_data_prop_items
                        )
            new_response_columns_setting.append(resp_column)
        return new_response_columns_setting


@dataclass
class BaseRequestSchema(BaseReferencialConfig):
    title: Optional[str] = None
    value_type: Optional[str] = None
    default: Optional[Any] = None
    ref: Optional[str] = None

    @abstractmethod
    def deserialize(self, data: dict) -> "BaseRequestSchema":
        pass


@dataclass
class _BaseRequestParameter(BaseReferencialConfig):
    name: str = field(default_factory=str)
    required: bool = False
    value_type: Optional[str] = None
    format: Optional[ApiDocValueFormat] = None
    enum: Optional[List[str]] = None
    default: Optional[Any] = None
    items: Optional[List["_BaseRequestParameter"]] = None
    schema: Optional["_BaseRequestParameter"] = None

    @abstractmethod
    def deserialize(self, data: dict) -> "_BaseRequestParameter":
        pass

    @abstractmethod
    def to_adapter(self) -> Optional[BaseRequestParameterAdapter]:
        pass


@dataclass
class BaseReferenceConfigProperty(BaseReferencialConfig):
    title: Optional[str] = None
    value_type: Optional[str] = None
    format: Optional[ApiDocValueFormat] = None  # For OpenAPI v3
    default: Optional[str] = None  # For OpenAPI v3 request part
    enums: List[str] = field(default_factory=list)
    ref: Optional[str] = None
    items: Optional["BaseReferenceConfigProperty"] = None
    additionalProperties: Optional["BaseReferenceConfigProperty"] = None

    @classmethod
    @abstractmethod
    def deserialize(cls, data: Dict) -> "BaseReferenceConfigProperty":
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        pass

    @abstractmethod
    def process_response_from_data(
        self,
        init_response: Optional[BaseResponsePropertyAdapter] = None,
    ) -> BaseResponsePropertyAdapter:
        pass


@dataclass
class BaseReferenceConfig(BaseAPIDocConfig):
    title: Optional[str] = None
    value_type: str = field(default_factory=str)  # unused
    required: Optional[List[str]] = None
    properties: Dict[str, BaseReferenceConfigProperty] = field(default_factory=dict)

    @classmethod
    @abstractmethod
    def deserialize(cls, data: Dict) -> "BaseReferenceConfig":
        pass

    @abstractmethod
    def process_reference_object(
        self,
        init_response: BaseResponsePropertyAdapter,
        empty_body_key: str = "",
    ) -> BaseResponsePropertyAdapter:
        pass


@dataclass
class BaseHttpConfigV2(BaseReferencialConfig):
    schema: Optional[BaseReferenceConfigProperty] = None

    @classmethod
    @abstractmethod
    def deserialize(cls, data: dict) -> "BaseHttpConfigV2":
        pass


@dataclass
class BaseHttpConfigV3(BaseAPIDocConfig):
    content: Optional[Dict[ContentType, BaseHttpConfigV2]] = None

    @classmethod
    @abstractmethod
    def deserialize(cls, data: dict) -> "BaseHttpConfigV3":
        pass

    @abstractmethod
    def exist_setting(self, content_type: Union[str, ContentType]) -> Optional[ContentType]:
        pass

    @abstractmethod
    def get_setting(self, content_type: Union[str, ContentType]) -> BaseHttpConfigV2:
        pass


@dataclass
class _BaseAPIConfigWithMethod(BaseAPIDocConfig, ABC):
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    operationId: str = field(default_factory=str)
    parameters: List[_BaseRequestParameter] = field(default_factory=list)
    responses: Dict[HTTPStatus, BaseAPIDocConfig] = field(default_factory=dict)

    @classmethod
    def deserialize(cls, data: dict) -> "_BaseAPIConfigWithMethod":
        request_config = [cls._deserialize_request(param) for param in data.get("parameters", [])]

        response = data.get("responses", {})
        response_config: Dict[HTTPStatus, BaseAPIDocConfig] = {}
        for status_code, resp_config in response.items():
            response_config[HTTPStatus(int(status_code))] = cls._deserialize_response(resp_config)

        return cls(
            tags=data.get("tags", []),
            summary=data.get("summary", ""),
            description=data.get("description", ""),
            operationId=data.get("operationId", ""),
            parameters=request_config,
            responses=response_config,
        )

    @staticmethod
    @abstractmethod
    def _deserialize_request(data: dict) -> _BaseRequestParameter:
        pass

    @staticmethod
    @abstractmethod
    def _deserialize_response(data: dict) -> BaseAPIDocConfig:
        pass

    @abstractmethod
    def to_request_adapter(self, http_method: str) -> List[BaseRequestParameterAdapter]:
        pass

    def _initial_request_parameters_model(
        self,
        _data: List[Union[_BaseRequestParameter, BaseHttpConfigV2]],
        not_ref_data: List[_BaseRequestParameter],
    ) -> List[BaseRequestParameterAdapter]:
        has_ref_in_schema_param = list(filter(lambda p: p.has_ref() != "", _data))
        handled_parameters = []
        if has_ref_in_schema_param:
            # TODO: Ensure the value maps this condition is really only one
            for d in _data:
                handled_parameters.extend(d.process_has_ref_request_parameters())
        else:
            for p in not_ref_data:
                adapter = p.to_adapter()
                if adapter:
                    handled_parameters.append(adapter)
        return handled_parameters

    def to_responses_adapter(self) -> BaseResponsePropertyAdapter:
        assert self.exist_in_response(status_code=200) is True
        status_200_response = self.get_response(status_code=200)
        tmp_resp_config = self._get_http_config(status_200_response)
        # Handle response config
        if tmp_resp_config.has_ref():
            response_data = tmp_resp_config.process_response_from_reference()
        else:
            # Data may '{}' or '{ "type": "integer", "title": "Id" }'
            tmp_resp_model = self._deserialize_empty_reference_config_properties()
            response_data = tmp_resp_model.process_response_from_data()
        return response_data

    @abstractmethod
    def _deserialize_empty_reference_config_properties(self) -> BaseReferenceConfigProperty:
        pass

    def exist_in_response(self, status_code: Union[int, HTTPStatus]) -> bool:
        return self._get_http_status(status_code) in self.responses.keys()

    def get_response(self, status_code: Union[int, HTTPStatus]) -> BaseAPIDocConfig:
        return self.responses[self._get_http_status(status_code)]

    def _get_http_status(self, status_code: Union[int, HTTPStatus]) -> HTTPStatus:
        return HTTPStatus(status_code) if isinstance(status_code, int) else status_code

    @abstractmethod
    def _get_http_config(self, status_200_response: BaseAPIDocConfig) -> BaseReferencialConfig:
        pass


@dataclass
class BaseAPIConfigWithMethodV2(_BaseAPIConfigWithMethod, ABC):
    produces: List[str] = field(default_factory=list)
    responses: Dict[HTTPStatus, BaseHttpConfigV2] = field(default_factory=dict)  # type: ignore[assignment]


@dataclass
class BaseAPIConfigWithMethodV3(_BaseAPIConfigWithMethod, ABC):
    request_body: Optional[BaseHttpConfigV3] = None
    responses: Dict[HTTPStatus, BaseHttpConfigV3] = field(default_factory=dict)  # type: ignore[assignment]


@dataclass
class BaseAPIConfig(BaseAPIDocConfig):
    api: Dict[HTTPMethod, _BaseAPIConfigWithMethod] = field(default_factory=dict)

    @abstractmethod
    def deserialize(self, data: dict) -> "BaseAPIConfig":
        pass

    @abstractmethod
    def to_adapter(self, path: str) -> List["BaseAPIAdapter"]:
        pass
