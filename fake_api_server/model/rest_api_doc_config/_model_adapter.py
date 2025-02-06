import logging
import sys
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple

from fake_api_server.model import MockAPI
from fake_api_server.model.api_config import IteratorItem
from fake_api_server.model.api_config.apis.request import (
    APIParameter as PyFake_RequestProperty,
)
from fake_api_server.model.api_config.apis.response import (
    ResponseProperty as PyFake_ResponseProperty,
)
from fake_api_server.model.api_config.apis.response_strategy import ResponseStrategy
from fake_api_server.model.api_config.format import Format as PyFake_Format

from ..api_config.value import FormatStrategy, ValueFormat
from ..api_config.variable import Digit, Size, Variable
from ._base_model_adapter import (
    BaseAPIAdapter,
    BaseFormatModelAdapter,
    BaseRefPropertyDetailAdapter,
    BaseRequestParameterAdapter,
    BaseResponsePropertyAdapter,
)
from ._js_handlers import ApiDocValueFormat, ensure_type_is_python_type
from .base_config import _BaseAPIConfigWithMethod, _Default_Required

logger = logging.getLogger(__name__)


@dataclass
class FormatAdapter(BaseFormatModelAdapter):

    def to_pyfake_api_config(self) -> Optional[PyFake_Format]:

        def _configure_customize(customize: str, value_format: ValueFormat) -> Tuple[str, List[Variable]]:
            cust = customize
            var = [Variable(name=cust, value_format=value_format)]
            return cust, var

        if self.enum:
            return PyFake_Format(
                strategy=FormatStrategy.FROM_ENUMS,
                enums=self.enum,
            )
        elif self.formatter:
            _strategy: FormatStrategy
            _digit: Optional[Digit] = None
            _size: Optional[Size] = None
            _customize: str = ""
            _variables: List[Variable] = []

            formatter = self.formatter.to_value_format()
            if formatter is ValueFormat.Integer:
                _strategy = FormatStrategy.BY_DATA_TYPE
                # TODO: It should have setting to configure this setting
                _size = Size(max_value=sys.maxsize, min_value=-sys.maxsize - 1)
            elif formatter is ValueFormat.BigDecimal:
                _strategy = FormatStrategy.BY_DATA_TYPE
                # TODO: It should have setting to configure this setting
                _digit = Digit(integer=100, decimal=50)
            elif formatter is ValueFormat.Date:
                _strategy = FormatStrategy.CUSTOMIZE
                (_customize, _variables) = _configure_customize("date_value", ValueFormat.Date)
            elif formatter is ValueFormat.DateTime:
                _strategy = FormatStrategy.CUSTOMIZE
                (_customize, _variables) = _configure_customize("datetime_value", ValueFormat.DateTime)
            elif formatter is ValueFormat.EMail:
                _strategy = FormatStrategy.CUSTOMIZE
                (_customize, _variables) = _configure_customize("email_value", ValueFormat.EMail)
            elif formatter is ValueFormat.UUID:
                _strategy = FormatStrategy.CUSTOMIZE
                (_customize, _variables) = _configure_customize("uuid_value", ValueFormat.UUID)
            elif formatter is ValueFormat.URI:
                _strategy = FormatStrategy.CUSTOMIZE
                (_customize, _variables) = _configure_customize("uri_value", ValueFormat.URI)
            elif formatter is ValueFormat.URL:
                _strategy = FormatStrategy.CUSTOMIZE
                (_customize, _variables) = _configure_customize("url_value", ValueFormat.URL)
            elif formatter is ValueFormat.IPv4:
                _strategy = FormatStrategy.CUSTOMIZE
                (_customize, _variables) = _configure_customize("ipv4_value", ValueFormat.IPv4)
            elif formatter is ValueFormat.IPv6:
                _strategy = FormatStrategy.CUSTOMIZE
                (_customize, _variables) = _configure_customize("ipv6_value", ValueFormat.IPv6)
            else:
                raise NotImplementedError

            return PyFake_Format(
                strategy=_strategy,
                # general setting
                digit=_digit,
                size=_size,
                # customize
                customize=_customize,
                variables=_variables,
            )
        else:
            return None


@dataclass
class PropertyDetailAdapter(BaseRefPropertyDetailAdapter):
    items: Optional[List["PropertyDetailAdapter"]] = None  # type: ignore[assignment]
    is_empty: Optional[bool] = None

    def _instantiate_obj(self, **kwargs) -> "PropertyDetailAdapter":
        return PropertyDetailAdapter(**kwargs)

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

    def to_pyfake_api_config(self) -> PyFake_ResponseProperty:
        return PyFake_ResponseProperty().deserialize(self.serialize())


@dataclass
class RequestParameterAdapter(BaseRequestParameterAdapter):
    items: Optional[List["RequestParameterAdapter"]] = None  # type: ignore[assignment]
    default: Optional[Any] = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.value_type:
            self.value_type = self._convert_value_type()

    def _instantiate_obj(self, **kwargs) -> "RequestParameterAdapter":
        return RequestParameterAdapter(**kwargs)

    def _convert_value_type(self) -> str:
        assert self.value_type
        return ensure_type_is_python_type(self.value_type)

    @classmethod
    def deserialize_by_prps(
        cls,
        name: str = "",
        required: bool = True,
        value_type: str = "",
        formatter: Optional[ApiDocValueFormat] = None,
        enum: Optional[List[str]] = None,
        default: Any = None,
        items: List["RequestParameterAdapter"] = [],
    ) -> "BaseRequestParameterAdapter":
        return RequestParameterAdapter(
            name=name,
            required=required,
            value_type=ensure_type_is_python_type(value_type) if value_type else None,
            format=FormatAdapter(
                formatter=formatter,
                enum=enum,
            ),
            default=default,
            items=items,
        )

    def to_pyfake_api_config(self) -> PyFake_RequestProperty:

        def to_items(item_data: BaseRequestParameterAdapter) -> IteratorItem:
            return IteratorItem(
                name=item_data.name,
                required=item_data.required,
                value_type=item_data.value_type,
                value_format=item_data.format.to_pyfake_api_config() if self.format else None,  # type: ignore[union-attr]
                items=[to_items(i) for i in (item_data.items or [])],
            )

        return PyFake_RequestProperty(
            name=self.name,
            required=self.required,
            value_type=self.value_type,
            default=self.default,
            value_format=self.format.to_pyfake_api_config() if self.format else None,
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
            parameters=list(map(lambda p: p.to_pyfake_api_config(), self.parameters)),
        )

        # Handle response config
        if list(filter(lambda p: p.name == "", self.response.data or [])):
            values = []
        else:
            values = self.response.data
        logger.debug(f"The values for converting to PyFake-API-Server format response config: {values}")
        resp_props_values = [p.to_pyfake_api_config() for p in values] if values else values
        mock_api.set_response(strategy=ResponseStrategy.OBJECT, iterable_value=resp_props_values)
        return mock_api
