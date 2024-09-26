from dataclasses import dataclass, field
from typing import Any, List, Optional, Union

from .. import MockAPI
from ..api_config import IteratorItem
from ..api_config.apis.request import APIParameter as PyMockRequestProperty
from ..api_config.apis.response import ResponseProperty as PyMockResponseProperty
from ..enums import ResponseStrategy
from ._js_handlers import ensure_type_is_python_type
from .base_config import (
    BaseAPIAdapter,
    BaseRefPropertyDetailAdapter,
    BaseRequestParameterAdapter,
    BaseResponsePropertyAdapter,
    _BaseTmpAPIDtailConfig,
    _BaseTmpRequestParameterModel,
    _Default_Required,
)


@dataclass
class PropertyDetailAdapter(BaseRefPropertyDetailAdapter):
    items: Optional[List["PropertyDetailAdapter"]] = None  # type: ignore[assignment]
    is_empty: Optional[bool] = None

    def serialize(self) -> dict:
        data = super().serialize()
        data["is_empty"] = self.is_empty
        return self._clear_empty_values(data)

    @staticmethod
    def generate_empty_response() -> "PropertyDetailAdapter":
        # if self is ResponseStrategy.OBJECT:
        return PropertyDetailAdapter(
            name="",
            required=_Default_Required.empty,
            value_type=None,
            format=None,
            items=[],
        )

    def to_pymock_api_config(self) -> PyMockResponseProperty:
        return PyMockResponseProperty().deserialize(self.serialize())


@dataclass
class RequestParameterAdapter(BaseRequestParameterAdapter):
    items: Optional[List[Union["BaseRequestParameterAdapter", _BaseTmpRequestParameterModel]]] = None
    default: Optional[Any] = None

    def __post_init__(self) -> None:
        if self.items is not None:
            self.items = self._convert_items()
        if self.value_type:
            self.value_type = self._convert_value_type()

    def _convert_items(self) -> List[Union["BaseRequestParameterAdapter", _BaseTmpRequestParameterModel]]:
        items: List[Union["BaseRequestParameterAdapter", _BaseTmpRequestParameterModel]] = []
        print(f"[DEBUG in RequestParameter._convert_items] items: {items}")
        for item in self.items or []:
            print(f"[DEBUG in RequestParameter._convert_items] item: {item}")
            assert isinstance(item, (BaseRequestParameterAdapter, _BaseTmpRequestParameterModel))
            items.append(item)
        return items

    def _convert_value_type(self) -> str:
        assert self.value_type
        return ensure_type_is_python_type(self.value_type)

    @classmethod
    def deserialize_by_prps(
        cls, name: str = "", required: bool = True, value_type: str = "", default: Any = None, items: List = []
    ) -> "BaseRequestParameterAdapter":
        return RequestParameterAdapter(
            name=name,
            required=required,
            value_type=ensure_type_is_python_type(value_type) if value_type else None,
            default=default,
            items=items,
        )

    def to_pymock_api_config(self) -> PyMockRequestProperty:

        def to_items(item_data: Union[BaseRequestParameterAdapter, _BaseTmpRequestParameterModel]) -> IteratorItem:
            if isinstance(item_data, RequestParameterAdapter):
                return IteratorItem(
                    name=item_data.name,
                    required=item_data.required,
                    value_type=item_data.value_type,
                    items=[to_items(i) for i in (item_data.items or [])],
                )
            elif isinstance(item_data, _BaseTmpRequestParameterModel):
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


@dataclass
class ResponsePropertyAdapter(BaseResponsePropertyAdapter):
    data: List[PropertyDetailAdapter] = field(default_factory=list)  # type: ignore[assignment]

    @staticmethod
    def initial_response_data() -> "ResponsePropertyAdapter":  # type: ignore[override]
        return ResponsePropertyAdapter(data=[])


@dataclass
class APIAdapter(BaseAPIAdapter):
    path: str = field(default_factory=str)
    http_method: str = field(default_factory=str)
    parameters: List[RequestParameterAdapter] = field(default_factory=list)  # type: ignore[assignment]
    response: ResponsePropertyAdapter = field(default_factory=ResponsePropertyAdapter)
    tags: Optional[List[str]] = None

    @classmethod
    def generate(cls, api_path: str, http_method: str, detail: _BaseTmpAPIDtailConfig) -> "APIAdapter":
        api = APIAdapter()
        api.path = api_path
        api.http_method = http_method
        api.deserialize(data=detail)
        return api

    def deserialize(self, data: _BaseTmpAPIDtailConfig) -> "APIAdapter":  # type: ignore[override]
        api_config: _BaseTmpAPIDtailConfig
        api_config = data
        self.parameters = api_config.process_api_parameters(http_method=self.http_method)  # type: ignore[assignment]
        self.response = api_config.process_responses()  # type: ignore[assignment]
        self.tags = api_config.tags

        return self

    def to_api_config(self, base_url: str = "") -> MockAPI:  # type: ignore[override]
        mock_api = MockAPI(url=self.path.replace(base_url, ""), tag=self.tags[0] if self.tags else "")

        # Handle request config
        mock_api.set_request(
            method=self.http_method.upper(),
            parameters=list(map(lambda p: p.to_pymock_api_config(), self.parameters)),
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
