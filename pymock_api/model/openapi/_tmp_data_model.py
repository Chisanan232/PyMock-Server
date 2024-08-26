import copy
import re
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from dataclasses import dataclass, field
from pydoc import locate
from typing import Any, Callable, Dict, List, Optional, Union

from ..api_config import IteratorItem
from ..api_config.apis.request import APIParameter as PyMockRequestProperty
from ..api_config.apis.response import ResponseProperty as PyMockResponseProperty
from ._base_schema_parser import BaseOpenAPISchemaParser
from ._js_handlers import ensure_type_is_python_type

ComponentDefinition: Dict[str, dict] = {}


def get_component_definition() -> Dict:
    global ComponentDefinition
    return ComponentDefinition


def set_component_definition(openapi_parser: BaseOpenAPISchemaParser) -> None:
    global ComponentDefinition
    ComponentDefinition = openapi_parser.get_objects()


_PropertyDefaultRequired = namedtuple("_PropertyDefaultRequired", ("empty", "general"))
_Default_Required: _PropertyDefaultRequired = _PropertyDefaultRequired(empty=False, general=True)


@dataclass
class BaseTmpDataModel(metaclass=ABCMeta):

    def _ensure_data_structure_when_object_strategy(
        self, init_response: "ResponseProperty", response_data_prop: Union["PropertyDetail", List["PropertyDetail"]]
    ) -> "PropertyDetail":
        print(f"[DEBUG in _ensure_data_structure_when_object_strategy] response_data_prop: {response_data_prop}")
        assert isinstance(response_data_prop, PropertyDetail)
        assert isinstance(
            init_response.data, list
        ), "The response data type must be *list* if its HTTP response strategy is object."
        assert (
            len(list(filter(lambda d: not isinstance(d, PropertyDetail), init_response.data))) == 0
        ), "Each column detail must be *dict* if its HTTP response strategy is object."
        return response_data_prop

    def _generate_response(
        self,
        init_response: "ResponseProperty",
        property_value: "TmpReferenceConfigPropertyModel",
    ) -> Union["PropertyDetail", List["PropertyDetail"]]:
        if property_value.is_empty():
            return PropertyDetail.generate_empty_response()
        print(f"[DEBUG in _generate_response] property_value: {property_value}")
        print(f"[DEBUG in _generate_response] before it have init_response: {init_response}")
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
        init_response: "ResponseProperty",
        resp_prop_data: Union["TmpReferenceConfigPropertyModel", "TmpConfigReferenceModel"],
    ) -> Union["PropertyDetail", List["PropertyDetail"]]:

        def _handle_list_type_data(
            data: TmpReferenceConfigPropertyModel,
            noref_val_process_callback: Callable,
            ref_val_process_callback: Callable,
            response: PropertyDetail = PropertyDetail(),
        ) -> PropertyDetail:
            items_data = data.items
            assert items_data
            if items_data.has_ref():
                response = _handle_reference_object(
                    response, items_data, noref_val_process_callback, ref_val_process_callback
                )
            else:
                print(f"[DEBUG in _handle_list_type_data] init_response: {init_response}")
                print(f"[DEBUG in _handle_list_type_data] items_data: {items_data}")
                response_item_value = self._generate_response_from_data(
                    init_response=init_response,
                    resp_prop_data=items_data,
                )
                print(f"[DEBUG in _handle_list_type_data] response_item_value: {response_item_value}")
                items = None
                if response_item_value:
                    items = response_item_value if isinstance(response_item_value, list) else [response_item_value]
                response = PropertyDetail(
                    name="",
                    required=_Default_Required.general,
                    value_type="list",
                    # TODO: Set the *format* property correctly
                    format=None,
                    items=items,
                )
                print(f"[DEBUG in _handle_list_type_data] response: {response}")
            return response

        def _handle_reference_object(
            response: PropertyDetail,
            items_data: TmpReferenceConfigPropertyModel,
            noref_val_process_callback: Callable[
                # item_k, item_v, response
                [str, TmpReferenceConfigPropertyModel, PropertyDetail],
                PropertyDetail,
            ],
            ref_val_process_callback: Callable[
                [
                    # item_k, item_v, response, single_response, noref_val_process_callback
                    str,
                    TmpReferenceConfigPropertyModel,
                    PropertyDetail,
                    TmpConfigReferenceModel,
                    Callable[
                        [str, TmpReferenceConfigPropertyModel, PropertyDetail],
                        PropertyDetail,
                    ],
                ],
                PropertyDetail,
            ],
        ) -> PropertyDetail:
            single_response: Optional[TmpConfigReferenceModel] = items_data.get_schema_ref()
            assert single_response
            for item_k, item_v in (single_response.properties or {}).items():
                print(f"[DEBUG in nested data issue at _handle_list_type_data] item_v: {item_v}")
                print(f"[DEBUG in nested data issue at _handle_list_type_data] response: {response}")
                if item_v.has_ref():
                    response = ref_val_process_callback(
                        item_k, item_v, response, single_response, noref_val_process_callback
                    )
                else:
                    response = noref_val_process_callback(item_k, item_v, response)
            return response

        def _handle_list_type_value_with_object_strategy(
            data: TmpReferenceConfigPropertyModel,
        ) -> PropertyDetail:

            def _ref_process_callback(
                item_k: str,
                item_v: TmpReferenceConfigPropertyModel,
                response: PropertyDetail,
                ref_single_response: TmpConfigReferenceModel,
                noref_val_process_callback: Callable[
                    [str, TmpReferenceConfigPropertyModel, PropertyDetail], PropertyDetail
                ],
            ) -> PropertyDetail:
                assert ref_single_response.required
                item_k_data_prop = PropertyDetail(
                    name=item_k,
                    required=item_k in ref_single_response.required,
                    value_type=item_v.value_type or "dict",
                    # TODO: Set the *format* property correctly
                    format=None,
                    items=[],
                )
                ref_item_v_response = _handle_reference_object(
                    items_data=item_v,
                    noref_val_process_callback=noref_val_process_callback,
                    ref_val_process_callback=_ref_process_callback,
                    response=item_k_data_prop,
                )
                print(
                    f"[DEBUG in nested data issue at _handle_list_type_data] ref_item_v_response from data which has reference object: {ref_item_v_response}"
                )
                print(
                    f"[DEBUG in nested data issue at _handle_list_type_data] response from data which has reference object: {response}"
                )
                print(f"[DEBUG in _handle_list_type_data] check whether the itme is empty or not: {response.items}")
                if response.items:
                    print("[DEBUG in _handle_list_type_data] the response item has data")
                    assert response.items and isinstance(response.items, list)
                    response.items.append(ref_item_v_response)
                else:
                    print("[DEBUG in _handle_list_type_data] the response item doesn't have data")
                    response.items = (
                        [ref_item_v_response] if not isinstance(ref_item_v_response, list) else ref_item_v_response
                    )
                return response

            def _noref_process_callback(
                item_k: str,
                item_v: TmpReferenceConfigPropertyModel,
                response_data_prop: PropertyDetail,
            ) -> PropertyDetail:
                item_type = item_v.value_type
                item = PropertyDetail(
                    name=item_k,
                    required=_Default_Required.general,
                    value_type=item_type,
                )
                assert isinstance(response_data_prop.items, list), "The data type of property *items* must be *list*."
                response_data_prop.items.append(item)
                return response_data_prop

            response_data_prop = PropertyDetail(
                name="",
                required=_Default_Required.general,
                value_type=v_type,
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
            data: Union[TmpReferenceConfigPropertyModel, TmpConfigReferenceModel]
        ) -> Union[PropertyDetail, List[PropertyDetail]]:
            print(f"[DEBUG in _handle_object_type_value_with_object_strategy] data: {data}")
            data_title = data.title
            if data_title:
                # TODO: It should also consider the scenario about input stream part (download file)
                # Example data: {'type': 'object', 'title': 'InputStream'}
                if re.search(data_title, "InputStream", re.IGNORECASE):
                    return PropertyDetail(
                        name="",
                        required=_Default_Required.general,
                        value_type="file",
                        # TODO: Set the *format* property correctly
                        format=None,
                        items=None,
                    )

            # Check reference first
            assert not isinstance(data, TmpConfigReferenceModel)
            has_ref = data.has_ref()
            if has_ref:
                # Process reference
                resp = data.process_response_from_reference(
                    init_response=init_response,
                )
                print("[DEBUG in _handle_object_type_value_with_object_strategy] has reference schema")
                print(f"[DEBUG in _handle_object_type_value_with_object_strategy] resp: {resp}")
                if has_ref == "additionalProperties":
                    return PropertyDetail(
                        name="additionalKey",
                        required=_Default_Required.general,
                        value_type="dict",
                        # TODO: Set the *format* property correctly
                        format=None,
                        items=resp.data,
                    )
                return resp.data
            else:
                # Handle the schema *additionalProperties*
                assert isinstance(data, TmpReferenceConfigPropertyModel)
                additional_properties = data.additionalProperties
                assert additional_properties
                additional_properties_type = additional_properties.value_type
                assert additional_properties_type
                if locate(additional_properties_type) in [list, dict, "file"]:
                    items_config_data = _handle_list_type_value_with_object_strategy(additional_properties)
                    print(
                        f"[DEBUG in _handle_object_type_value_with_object_strategy] items_config_data: {items_config_data}"
                    )
                    # Collection type config has been wrap one level of *additionalKey*. So it doesn't need to wrap
                    # it again.
                    return items_config_data
                else:
                    return PropertyDetail(
                        name="",
                        required=_Default_Required.general,
                        value_type="dict",
                        # TODO: Set the *format* property correctly
                        format=None,
                        items=[
                            PropertyDetail(
                                name="additionalKey",
                                required=_Default_Required.general,
                                value_type=additional_properties_type,
                                # TODO: Set the *format* property correctly
                                format=None,
                                items=None,
                            ),
                        ],
                    )

        def _handle_other_types_value_with_object_strategy(v_type: str) -> PropertyDetail:
            return PropertyDetail(
                name="",
                required=_Default_Required.general,
                value_type=v_type,
                # TODO: Set the *format* property correctly
                format=None,
                items=None,
            )

        def _handle_each_data_types_response_with_object_strategy(
            data: Union[TmpReferenceConfigPropertyModel, TmpConfigReferenceModel], v_type: str
        ) -> Union[PropertyDetail, List[PropertyDetail]]:
            if locate(v_type) == list:
                assert isinstance(data, TmpReferenceConfigPropertyModel)
                return _handle_list_type_value_with_object_strategy(data)
            elif locate(v_type) == dict:
                return _handle_object_type_value_with_object_strategy(data)
            else:
                print(f"[DEBUG in src._handle_each_data_types_response_with_object_strategy] v_type: {v_type}")
                print(f"[DEBUG in src._handle_each_data_types_response_with_object_strategy] data: {data}")
                return _handle_other_types_value_with_object_strategy(v_type)

        print(f"[DEBUG in _handle_not_ref_data] resp_prop_data: {resp_prop_data}")
        if not resp_prop_data.value_type:
            assert not isinstance(resp_prop_data, TmpConfigReferenceModel)
            assert resp_prop_data.has_ref()
            return _handle_each_data_types_response_with_object_strategy(resp_prop_data, "dict")
        v_type = resp_prop_data.value_type
        return _handle_each_data_types_response_with_object_strategy(resp_prop_data, v_type)


@dataclass
class BaseTmpRefDataModel(BaseTmpDataModel):

    @abstractmethod
    def has_ref(self) -> str:
        pass

    @abstractmethod
    def get_ref(self) -> str:
        pass

    def get_schema_ref(self) -> "TmpConfigReferenceModel":
        def _get_schema(component_def_data: dict, paths: List[str], i: int) -> dict:
            if i == len(paths) - 1:
                return component_def_data[paths[i]]
            else:
                return _get_schema(component_def_data[paths[i]], paths, i + 1)

        print(f"[DEBUG in get_schema_ref] self: {self}")
        _has_ref = self.has_ref()
        print(f"[DEBUG in get_schema_ref] _has_ref: {_has_ref}")
        if not _has_ref:
            raise ValueError("This parameter has no ref in schema.")
        schema_path = self.get_ref().replace("#/", "").split("/")[1:]
        print(f"[DEBUG in get_schema_ref] schema_path: {schema_path}")
        # Operate the component definition object
        return TmpConfigReferenceModel.deserialize(_get_schema(get_component_definition(), schema_path, 0))

    def process_response_from_reference(
        self,
        init_response: Optional["ResponseProperty"] = None,
    ) -> "ResponseProperty":
        if not init_response:
            init_response = ResponseProperty.initial_response_data()
        response = self.get_schema_ref().process_reference_object(init_response=init_response)

        # Handle the collection data which has empty body
        new_response = copy.copy(response)
        response_columns_setting = response.data or []
        new_response.data = self._process_empty_body_response(response_columns_setting=response_columns_setting)
        response = new_response

        return response

    def _process_empty_body_response(self, response_columns_setting: List["PropertyDetail"]) -> List["PropertyDetail"]:
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
class TmpRequestSchemaModel(BaseTmpRefDataModel):
    title: Optional[str] = None
    value_type: Optional[str] = None
    default: Optional[Any] = None
    ref: Optional[str] = None

    def deserialize(self, data: dict) -> "TmpRequestSchemaModel":
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


@dataclass
class TmpRequestParameterModel(BaseTmpRefDataModel):
    name: str = field(default_factory=str)
    required: bool = False
    value_type: Optional[str] = None
    format: Optional[dict] = None
    default: Optional[Any] = None
    items: Optional[List["TmpRequestParameterModel"]] = None
    schema: Optional["TmpRequestSchemaModel"] = None

    def _convert_items(self) -> List[Union["TmpRequestParameterModel"]]:
        assert self.items
        if True in list(  # type: ignore[comparison-overlap]
            filter(lambda e: not isinstance(e, (dict, TmpRequestParameterModel)), self.items)
        ):
            raise ValueError(
                f"There are some invalid data type item in the property *items*. Current *items*: {self.items}"
            )
        return [TmpRequestParameterModel().deserialize(i) if isinstance(i, dict) else i for i in (self.items or [])]  # type: ignore[arg-type]

    def deserialize(self, data: dict) -> "TmpRequestParameterModel":
        print(f"[DEBUG in TmpRequestParameterModel.deserialize] data: {data}")
        self.name = data.get("name", "")
        self.required = data.get("required", True)

        items = data.get("items", [])
        if items:
            self.items = items if isinstance(items, list) else [items]
            self.items = self._convert_items()

        schema = data.get("schema", {})
        if schema:
            self.schema = TmpRequestSchemaModel().deserialize(schema)

        print(f"[DEBUG in TmpRequestParameterModel.deserialize] self.schema: {self.schema}")
        self.value_type = ensure_type_is_python_type(data.get("type", "")) or (
            self.schema.value_type if self.schema else ""
        )
        self.default = data.get("default", None) or (self.schema.default if self.schema else None)
        print(f"[DEBUG in TmpRequestParameterModel.deserialize] self: {self}")
        return self

    def has_ref(self) -> str:
        return "schema" if self.schema and self.schema.has_ref() else ""

    def get_ref(self) -> str:
        assert self.schema
        return self.schema.get_ref()


@dataclass
class TmpReferenceConfigPropertyModel(BaseTmpRefDataModel):
    title: Optional[str] = None
    value_type: Optional[str] = None
    format: Optional[str] = None  # For OpenAPI v3
    default: Optional[str] = None  # For OpenAPI v3 request part
    enums: List[str] = field(default_factory=list)
    ref: Optional[str] = None
    items: Optional["TmpReferenceConfigPropertyModel"] = None
    additionalProperties: Optional["TmpReferenceConfigPropertyModel"] = None

    @classmethod
    def deserialize(cls, data: Dict) -> "TmpReferenceConfigPropertyModel":
        print(f"[DEBUG in TmpResponsePropertyModel.deserialize] data: {data}")
        return TmpReferenceConfigPropertyModel(
            title=data.get("title", None),
            value_type=ensure_type_is_python_type(data["type"]) if data.get("type", None) else None,
            format="",  # TODO: Support in next PR
            default=data.get("default", None),
            enums=[],  # TODO: Support in next PR
            ref=data.get("$ref", None),
            items=TmpReferenceConfigPropertyModel.deserialize(data["items"]) if data.get("items", None) else None,
            additionalProperties=(
                TmpReferenceConfigPropertyModel.deserialize(data["additionalProperties"])
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
        init_response: Optional["ResponseProperty"] = None,
    ) -> "ResponseProperty":
        if not init_response:
            init_response = ResponseProperty.initial_response_data()
        response_config = self._generate_response(
            init_response=init_response,
            property_value=self,
        )
        response_data_prop = self._ensure_data_structure_when_object_strategy(init_response, response_config)
        init_response.data.append(response_data_prop)
        return init_response


@dataclass
class TmpConfigReferenceModel(BaseTmpDataModel):
    title: Optional[str] = None
    value_type: str = field(default_factory=str)  # unused
    required: Optional[list[str]] = None
    properties: Dict[str, TmpReferenceConfigPropertyModel] = field(default_factory=dict)

    @classmethod
    def deserialize(cls, data: Dict) -> "TmpConfigReferenceModel":
        print(f"[DEBUG in TmpResponseModel.deserialize] data: {data}")
        properties = {}
        properties_config: dict = data.get("properties", {})
        if properties_config:
            for k, v in properties_config.items():
                properties[k] = TmpReferenceConfigPropertyModel.deserialize(v)
        return TmpConfigReferenceModel(
            title=data.get("title", None),
            value_type=ensure_type_is_python_type(data["type"]) if data.get("type", None) else "",
            required=data.get("required", None),
            properties=properties,
        )

    def process_reference_object(
        self,
        init_response: "ResponseProperty",
        empty_body_key: str = "",
    ) -> "ResponseProperty":
        # assert response_schema_ref
        response_schema_properties: Dict[str, TmpReferenceConfigPropertyModel] = self.properties or {}
        print(f"[DEBUG in process_response_from_reference] response_schema_ref: {self}")
        print(f"[DEBUG in process_response_from_reference] response_schema_properties: {response_schema_properties}")
        if response_schema_properties:
            for k, v in response_schema_properties.items():
                print(f"[DEBUG in process_response_from_reference] k: {k}")
                print(f"[DEBUG in process_response_from_reference] v: {v}")
                # Check reference again
                if v.has_ref():
                    response_prop = v.get_schema_ref().process_reference_object(
                        init_response=ResponseProperty.initial_response_data(),
                        empty_body_key=k,
                    )
                    print(f"[DEBUG in process_response_from_reference] before asserion, response_prop: {response_prop}")
                    # TODO: It should have better way to handle output streaming
                    if len(list(filter(lambda d: d.value_type == "file", response_prop.data))) != 0:
                        # It's file inputStream
                        response_config = response_prop.data[0]
                    else:
                        response_config = PropertyDetail(
                            name="",
                            required=_Default_Required.empty,
                            value_type="dict",
                            format=None,
                            items=response_prop.data,
                        )
                else:
                    response_config = self._generate_response(  # type: ignore[assignment]
                        init_response=init_response,
                        property_value=v,
                    )
                print(f"[DEBUG in process_response_from_reference] response_config: {response_config}")
                response_data_prop = self._ensure_data_structure_when_object_strategy(init_response, response_config)
                print(
                    f"[DEBUG in process_response_from_reference] has properties, response_data_prop: {response_data_prop}"
                )
                response_data_prop.name = k
                response_data_prop.required = k in (self.required or [k])
                init_response.data.append(response_data_prop)
            print(f"[DEBUG in process_response_from_reference] parse with body, init_response: {init_response}")
        else:
            # The section which doesn't have setting body
            response_config = PropertyDetail.generate_empty_response()
            if self.title == "InputStream":
                response_config.value_type = "file"

                response_data_prop = self._ensure_data_structure_when_object_strategy(init_response, response_config)
                print(
                    f"[DEBUG in process_response_from_reference] doesn't have properties, response_data_prop: {response_data_prop}"
                )
                response_data_prop.name = empty_body_key
                response_data_prop.required = empty_body_key in (self.required or [empty_body_key])
                init_response.data.append(response_data_prop)
            else:
                response_data_prop = self._ensure_data_structure_when_object_strategy(init_response, response_config)
                print(
                    f"[DEBUG in process_response_from_reference] doesn't have properties, response_data_prop: {response_data_prop}"
                )
                response_data_prop.name = "THIS_IS_EMPTY"
                response_data_prop.required = False
                init_response.data.append(response_data_prop)
                print(f"[DEBUG in process_response_from_reference] empty_body_key: {empty_body_key}")
                print(
                    f"[DEBUG in process_response_from_reference] parse with empty body, init_response: {init_response}"
                )
        return init_response


@dataclass
class TmpHttpConfigV2(BaseTmpRefDataModel):
    schema: Optional[TmpReferenceConfigPropertyModel] = None
    content: Optional[dict] = None

    @classmethod
    def deserialize(cls, data: dict) -> "TmpHttpConfigV2":
        assert data is not None and isinstance(data, dict)
        return TmpHttpConfigV2(
            schema=TmpReferenceConfigPropertyModel.deserialize(data.get("schema", {})),
            content=data.get("content", None),
        )

    def has_ref(self) -> str:
        return "schema" if self.schema and self.schema.has_ref() else ""

    def get_ref(self) -> str:
        assert self.has_ref()
        assert self.schema.ref  # type: ignore[union-attr]
        return self.schema.ref  # type: ignore[union-attr]

    def is_empty(self) -> bool:
        return not self.schema or self.schema.is_empty()


# The base data model for request and response
@dataclass
class BasePropertyDetail(metaclass=ABCMeta):
    name: str = field(default_factory=str)
    required: bool = False
    value_type: Optional[str] = None
    format: Optional[dict] = None
    items: Optional[List["BasePropertyDetail"]] = None

    def serialize(self) -> dict:
        data = {
            "name": self.name,
            "required": self.required,
            "type": self.value_type,
            "format": self.format,
            "items": [item.serialize() for item in self.items] if self.items else None,
        }
        return self._clear_empty_values(data)

    def _clear_empty_values(self, data):
        new_data = {}
        for k, v in data.items():
            if v is not None:
                new_data[k] = v
        return new_data

    @abstractmethod
    def to_pymock_api_config(self) -> Union[PyMockRequestProperty, PyMockResponseProperty]:
        pass


# The data models for final result which would be converted as the data models of PyMock-API configuration
@dataclass
class PropertyDetail(BasePropertyDetail):
    items: Optional[List["PropertyDetail"]] = None  # type: ignore[assignment]
    is_empty: Optional[bool] = None

    def serialize(self) -> dict:
        data = super().serialize()
        data["is_empty"] = self.is_empty
        return self._clear_empty_values(data)

    @staticmethod
    def generate_empty_response() -> "PropertyDetail":
        # if self is ResponseStrategy.OBJECT:
        return PropertyDetail(
            name="",
            required=_Default_Required.empty,
            value_type=None,
            format=None,
            items=[],
        )

    def to_pymock_api_config(self) -> PyMockResponseProperty:
        return PyMockResponseProperty().deserialize(self.serialize())


# The tmp data model for final result to convert as PyMock-API
@dataclass
class RequestParameter(BasePropertyDetail):
    items: Optional[List[Union["RequestParameter", TmpRequestParameterModel]]] = None  # type: ignore[assignment]
    default: Optional[Any] = None

    def __post_init__(self) -> None:
        if self.items is not None:
            self.items = self._convert_items()
        if self.value_type:
            self.value_type = self._convert_value_type()

    def _convert_items(self) -> List[Union["RequestParameter", TmpRequestParameterModel]]:
        items: List[Union["RequestParameter", TmpRequestParameterModel]] = []
        print(f"[DEBUG in RequestParameter._convert_items] items: {items}")
        for item in self.items or []:
            print(f"[DEBUG in RequestParameter._convert_items] item: {item}")
            assert isinstance(item, (RequestParameter, TmpRequestParameterModel))
            items.append(item)
        return items

    def _convert_value_type(self) -> str:
        assert self.value_type
        return ensure_type_is_python_type(self.value_type)

    @classmethod
    def deserialize_by_prps(
        cls, name: str = "", required: bool = True, value_type: str = "", default: Any = None, items: List = []
    ) -> "RequestParameter":
        return RequestParameter(
            name=name,
            required=required,
            value_type=ensure_type_is_python_type(value_type) if value_type else None,
            default=default,
            items=items,
        )

    def to_pymock_api_config(self) -> PyMockRequestProperty:

        def to_items(item_data: Union[RequestParameter, TmpRequestParameterModel]) -> IteratorItem:
            if isinstance(item_data, RequestParameter):
                return IteratorItem(
                    name=item_data.name,
                    required=item_data.required,
                    value_type=item_data.value_type,
                    items=[to_items(i) for i in (item_data.items or [])],
                )
            elif isinstance(item_data, TmpRequestParameterModel):
                return IteratorItem(
                    name=item_data.name,
                    required=item_data.required,
                    value_type=item_data.value_type,
                    items=[to_items(i) for i in (item_data.items or [])],
                )
            else:
                raise TypeError(
                    f"The data model must be *TmpAPIParameterModel* or *TmpItemModel*. But it get *{item_data}*. Please check it."
                )

        return PyMockRequestProperty(
            name=self.name,
            required=self.required,
            value_type=self.value_type,
            default=self.default,
            value_format=None,
            items=[to_items(i) for i in (self.items or [])],
        )


# Just for temporarily use in data process
@dataclass
class ResponseProperty:
    data: List[PropertyDetail] = field(default_factory=list)

    @staticmethod
    def initial_response_data() -> "ResponseProperty":
        return ResponseProperty(data=[])
