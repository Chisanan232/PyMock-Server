import logging
from dataclasses import dataclass, field
from typing import Any, List, Optional

from pymock_server.model import MockAPI
from pymock_server.model.api_config import IteratorItem
from pymock_server.model.api_config.apis.request import (
    APIParameter as PyMockRequestProperty,
)
from pymock_server.model.api_config.apis.response import (
    ResponseProperty as PyMockResponseProperty,
)
from pymock_server.model.api_config.apis.response_strategy import ResponseStrategy

from ._base_model_adapter import (
    BaseAPIAdapter,
    BaseRefPropertyDetailAdapter,
    BaseRequestParameterAdapter,
    BaseResponsePropertyAdapter,
)
from ._js_handlers import ensure_type_is_python_type
from .base_config import _BaseAPIConfigWithMethod, _Default_Required

logger = logging.getLogger(__name__)


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
    items: Optional[List["RequestParameterAdapter"]] = None  # type: ignore[assignment]
    default: Optional[Any] = None

    def __post_init__(self) -> None:
        if self.items is not None:
            self.items = self._convert_items()
        if self.value_type:
            self.value_type = self._convert_value_type()

    def _convert_items(self) -> List["RequestParameterAdapter"]:
        items: List["RequestParameterAdapter"] = []
        for item in self.items or []:
            assert isinstance(item, RequestParameterAdapter)
            items.append(item)
        return items

    def _convert_value_type(self) -> str:
        assert self.value_type
        return ensure_type_is_python_type(self.value_type)

    @classmethod
    def deserialize_by_prps(
        cls,
        name: str = "",
        required: bool = True,
        value_type: str = "",
        default: Any = None,
        items: List["RequestParameterAdapter"] = [],
    ) -> "BaseRequestParameterAdapter":
        return RequestParameterAdapter(
            name=name,
            required=required,
            value_type=ensure_type_is_python_type(value_type) if value_type else None,
            default=default,
            items=items,
        )

    def to_pymock_api_config(self) -> PyMockRequestProperty:

        def to_items(item_data: BaseRequestParameterAdapter) -> IteratorItem:
            return IteratorItem(
                name=item_data.name,
                required=item_data.required,
                value_type=item_data.value_type,
                items=[to_items(i) for i in (item_data.items or [])],
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
    def generate(cls, api_path: str, http_method: str, detail: _BaseAPIConfigWithMethod) -> "APIAdapter":
        api = APIAdapter()
        api.path = api_path
        api.http_method = http_method
        api.deserialize(data=detail)
        return api

    def deserialize(self, data: _BaseAPIConfigWithMethod) -> "APIAdapter":  # type: ignore[override]
        self.parameters = data.to_request_adapter(http_method=self.http_method)  # type: ignore[assignment]
        self.response = data.to_responses_adapter()  # type: ignore[assignment]
        self.tags = data.tags
        return self

    def to_api_config(self, base_url: str = "") -> MockAPI:  # type: ignore[override]
        mock_api = MockAPI(url=self.path.replace(base_url, ""), tag=self.tags[0] if self.tags else "")

        # Handle request config
        mock_api.set_request(
            method=self.http_method.upper(),
            parameters=list(map(lambda p: p.to_pymock_api_config(), self.parameters)),
        )

        # Handle response config
        if list(filter(lambda p: p.name == "", self.response.data or [])):
            values = []
        else:
            values = self.response.data
        logger.debug(f"The values for converting to PyMock-Server format response config: {values}")
        resp_props_values = [p.to_pymock_api_config() for p in values] if values else values
        mock_api.set_response(strategy=ResponseStrategy.OBJECT, iterable_value=resp_props_values)
        return mock_api
