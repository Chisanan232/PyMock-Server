from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from ._js_handlers import ensure_type_is_python_type


@dataclass
class BaseTmpDataModel(metaclass=ABCMeta):
    pass


@dataclass
class BaseTmpRefDataModel(BaseTmpDataModel):

    @abstractmethod
    def has_ref(self) -> bool:
        pass


@dataclass
class TmpRequestItemModel(BaseTmpRefDataModel):
    title: Optional[str] = None
    value_type: Optional[str] = None
    format: Optional[str] = None
    enums: List[str] = field(default_factory=list)
    ref: Optional[str] = None

    @classmethod
    def deserialize(cls, data: Dict) -> "TmpRequestItemModel":
        print(f"[DEBUG in TmpRequestItemModel.deserialize] data: {data}")
        return TmpRequestItemModel(
            title=data.get("title", None),
            value_type=ensure_type_is_python_type(data["type"]) if data.get("type", None) else None,
            format="",  # TODO: Support in next PR
            enums=[],  # TODO: Support in next PR
            ref=data.get("$ref", None),
        )

    def has_ref(self) -> bool:
        return True if self.ref else False


@dataclass
class TmpAPIParameterModel(BaseTmpDataModel):
    name: str = field(default_factory=str)
    required: bool = False
    value_type: str = field(default_factory=str)
    default: Optional[str] = None
    items: Optional[List[Union["TmpAPIParameterModel", TmpRequestItemModel]]] = None

    def __post_init__(self) -> None:
        if self.items is not None:
            self.items = self._convert_items()
        if self.value_type:
            self.value_type = self._convert_value_type()

    def _convert_items(self) -> List[Union["TmpAPIParameterModel", TmpRequestItemModel]]:
        items: List[Union[TmpAPIParameterModel, TmpRequestItemModel]] = []
        for item in self.items or []:
            assert isinstance(item, (TmpAPIParameterModel, TmpRequestItemModel))
            items.append(item)
        return items

    def _convert_value_type(self) -> str:
        return ensure_type_is_python_type(self.value_type)


@dataclass
class TmpResponsePropertyModel(BaseTmpRefDataModel):
    title: Optional[str] = None
    value_type: Optional[str] = None
    format: Optional[str] = None  # For OpenAPI v3
    enums: List[str] = field(default_factory=list)
    ref: Optional[str] = None
    items: Optional["TmpResponsePropertyModel"] = None
    additionalProperties: Optional["TmpResponsePropertyModel"] = None

    @classmethod
    def deserialize(cls, data: Dict) -> "TmpResponsePropertyModel":
        print(f"[DEBUG in TmpResponsePropertyModel.deserialize] data: {data}")
        return TmpResponsePropertyModel(
            title=data.get("title", None),
            value_type=ensure_type_is_python_type(data["type"]) if data.get("type", None) else None,
            format="",  # TODO: Support in next PR
            enums=[],  # TODO: Support in next PR
            ref=data.get("$ref", None),
            items=TmpResponsePropertyModel.deserialize(data["items"]) if data.get("items", None) else None,
            additionalProperties=(
                TmpResponsePropertyModel.deserialize(data["additionalProperties"])
                if data.get("additionalProperties", None)
                else None
            ),
        )

    def has_ref(self) -> bool:
        return (
            True
            if (
                self.ref
                or (self.items and self.items.has_ref())
                or (self.additionalProperties and self.additionalProperties.has_ref())
            )
            else False
        )

    def is_empty(self) -> bool:
        return not (self.value_type or self.ref)


@dataclass
class TmpResponseRefModel(BaseTmpDataModel):
    title: Optional[str] = None
    value_type: str = field(default_factory=str)  # unused
    required: Optional[list[str]] = None
    properties: Dict[str, TmpResponsePropertyModel] = field(default_factory=dict)

    @classmethod
    def deserialize(cls, data: Dict) -> "TmpResponseRefModel":
        print(f"[DEBUG in TmpResponseModel.deserialize] data: {data}")
        properties = {}
        properties_config: dict = data.get("properties", {})
        if properties_config:
            for k, v in properties_config.items():
                properties[k] = TmpResponsePropertyModel.deserialize(v)
        return TmpResponseRefModel(
            title=data.get("title", None),
            value_type=ensure_type_is_python_type(data["type"]) if data.get("type", None) else "",
            required=data.get("required", None),
            properties=properties,
        )


@dataclass
class TmpResponseSchema(BaseTmpRefDataModel):
    schema: Optional[TmpResponsePropertyModel] = None

    @classmethod
    def deserialize(cls, data: dict) -> "TmpResponseSchema":
        if data:
            return TmpResponseSchema(schema=TmpResponsePropertyModel.deserialize(data.get("schema", {})))
        return TmpResponseSchema()

    def has_ref(self) -> bool:
        return True if self.schema and self.schema.has_ref else False  # type: ignore[truthy-function]

    def is_empty(self) -> bool:
        return not self.schema or self.schema.is_empty()


# The data models for final result which would be converted as the data models of PyMock-API configuration
@dataclass
class PropertyDetail:
    name: str = field(default_factory=str)
    required: bool = False
    type: Optional[str] = None
    format: Optional[dict] = None
    items: Optional[List["PropertyDetail"]] = None
    is_empty: Optional[bool] = None

    def serialize(self) -> dict:
        data = {
            "name": self.name,
            "required": self.required,
            "type": self.type,
            "format": self.format,
            "is_empty": self.is_empty,
            "items": [item.serialize() for item in self.items] if self.items else None,
        }
        new_data = {}
        for k, v in data.items():
            if v is not None:
                new_data[k] = v
        return new_data


# Just for temporarily use in data process
@dataclass
class ResponseProperty:
    data: List[PropertyDetail] = field(default_factory=list)

    @classmethod
    def deserialize(cls, data: Dict) -> "ResponseProperty":
        print(f"[DEBUG in ResponseProperty.deserialize] data: {data}")
        return ResponseProperty(
            data=data["data"],
        )
