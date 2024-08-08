from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from ._js_handlers import ensure_type_is_python_type


@dataclass
class BaseTmpDataModel:
    pass


@dataclass
class TmpItemModel(BaseTmpDataModel):
    value_type: str = field(default_factory=str)
    format: Optional[str] = None
    enums: List[str] = field(default_factory=list)
    ref: str = field(default_factory=str)

    @classmethod
    def deserialize(cls, data: Dict) -> "TmpItemModel":
        print(f"[DEBUG in TmpItemModel.deserialize] data: {data}")
        return TmpItemModel(
            value_type=ensure_type_is_python_type(data["type"]),
            format="",  # TODO: Support in next PR
            enums=[],  # TODO: Support in next PR
            ref="",  # TODO: Support in next PR
        )


@dataclass
class TmpAPIParameterModel(BaseTmpDataModel):
    name: str = field(default_factory=str)
    required: bool = False
    value_type: str = field(default_factory=str)
    default: Optional[str] = None
    items: Optional[List[Union["TmpAPIParameterModel", TmpItemModel]]] = None

    def __post_init__(self) -> None:
        if self.items is not None:
            self.items = self._convert_items()
        if self.value_type:
            self.value_type = self._convert_value_type()

    def _convert_items(self) -> List[Union["TmpAPIParameterModel", TmpItemModel]]:
        items: List[Union[TmpAPIParameterModel, TmpItemModel]] = []
        for item in self.items or []:
            assert isinstance(item, (TmpAPIParameterModel, TmpItemModel))
            items.append(item)
        return items

    def _convert_value_type(self) -> str:
        return ensure_type_is_python_type(self.value_type)


@dataclass
class TmpResponsePropertyModel(BaseTmpDataModel):
    value_type: Optional[str] = None
    format: Optional[str] = None  # For OpenAPI v3
    enums: List[str] = field(default_factory=list)
    ref: str = field(default_factory=str)
    items: Optional[TmpItemModel] = None

    @classmethod
    def deserialize(cls, data: Dict) -> "TmpResponsePropertyModel":
        print(f"[DEBUG in TmpItemModel.deserialize] data: {data}")
        return TmpResponsePropertyModel(
            value_type=ensure_type_is_python_type(data["type"]) if data.get("type", None) else None,
            format="",  # TODO: Support in next PR
            enums=[],  # TODO: Support in next PR
            ref="",  # TODO: Support in next PR
            items=None,
        )


@dataclass
class TmpResponseModel(BaseTmpDataModel):
    value_type: str = field(default_factory=str)  # unused
    required: list[str] = field(default_factory=list)
    properties: dict[str, TmpResponsePropertyModel] = field(default_factory=dict)


@dataclass
class TmpResponseSchema(BaseTmpDataModel):
    schema: Optional[TmpResponsePropertyModel] = None

    @classmethod
    def deserialize(cls, data: dict) -> "TmpResponseSchema":
        if data:
            return TmpResponseSchema(schema=TmpResponsePropertyModel.deserialize(data.get("schema", {})))
        return TmpResponseSchema()


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
