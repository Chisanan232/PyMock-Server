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
