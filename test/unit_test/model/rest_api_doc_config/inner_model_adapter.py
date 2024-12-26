import logging
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from typing import List, Optional, Type, Union

import pytest

from pymock_server.model import APIParameter
from pymock_server.model.api_config.apis import ResponseStrategy
from pymock_server.model.api_config.apis._property import BaseProperty
from pymock_server.model.api_config.format import Format
from pymock_server.model.api_config.value import FormatStrategy, ValueFormat
from pymock_server.model.api_config.variable import Size, Variable
from pymock_server.model.rest_api_doc_config._base_model_adapter import (
    BasePropertyDetailAdapter,
)
from pymock_server.model.rest_api_doc_config._js_handlers import ApiDocValueFormat
from pymock_server.model.rest_api_doc_config._model_adapter import (
    FormatAdapter,
    PropertyDetailAdapter,
    RequestParameterAdapter,
)

logger = logging.getLogger(__name__)


def _adapter_config(
    required: bool,
    value_type: str,
    name: Optional[str] = None,
    format: Optional[FormatAdapter] = None,
    items: Optional[List[dict]] = None,
) -> dict:
    return {
        "name": name,
        "required": required,
        "value_type": value_type,
        "format": format,
        "items": items,
    }


ExpectModelProps = namedtuple("ExpectModelProps", ("name", "required", "value_type", "format", "items"))


class _BaseTestSuite(metaclass=ABCMeta):
    @abstractmethod
    @pytest.fixture(scope="function")
    def adapter_model_obj(self) -> Type[BasePropertyDetailAdapter]:
        pass

    @abstractmethod
    @pytest.fixture(scope="function")
    def pymock_model(self) -> BaseProperty:
        pass

    @pytest.mark.parametrize(
        ("under_test_data", "expect"),
        [
            (
                _adapter_config(name="param", required=True, value_type="str"),
                ExpectModelProps(name="param", required=True, value_type="str", format=None, items=None),
            ),
            (
                _adapter_config(name="param", required=False, value_type="int"),
                ExpectModelProps(name="param", required=False, value_type="int", format=None, items=None),
            ),
            (
                _adapter_config(name="param", required=False, value_type="list"),
                ExpectModelProps(name="param", required=False, value_type="list", format=None, items=None),
            ),
            (
                _adapter_config(
                    name="param",
                    required=True,
                    value_type="str",
                    format=FormatAdapter(formatter=ApiDocValueFormat.Int32),
                ),
                ExpectModelProps(
                    name="param",
                    required=True,
                    value_type="str",
                    format=Format(
                        strategy=FormatStrategy.BY_DATA_TYPE,
                        size=Size(max_value=9223372036854775807, min_value=-9223372036854775808),
                    ),
                    items=None,
                ),
            ),
            (
                _adapter_config(
                    name="param", required=True, value_type="str", format=FormatAdapter(enum=["TYPE_1", "TYPE_2"])
                ),
                ExpectModelProps(
                    name="param",
                    required=True,
                    value_type="str",
                    format=Format(strategy=FormatStrategy.FROM_ENUMS, enums=["TYPE_1", "TYPE_2"]),
                    items=None,
                ),
            ),
            (
                _adapter_config(
                    name="param",
                    required=True,
                    value_type="str",
                    format=FormatAdapter(formatter=ApiDocValueFormat.DateTime),
                ),
                ExpectModelProps(
                    name="param",
                    required=True,
                    value_type="str",
                    format=Format(
                        strategy=FormatStrategy.CUSTOMIZE,
                        customize="datetime_value",
                        variables=[Variable(name="datetime_value", value_format=ValueFormat.DateTime)],
                    ),
                    items=None,
                ),
            ),
            (
                _adapter_config(
                    name="array_param",
                    required=True,
                    value_type="list",
                    format=None,
                    items=[
                        _adapter_config(
                            required=True,
                            value_type="str",
                            format=FormatAdapter(formatter=ApiDocValueFormat.DateTime),
                        ),
                    ],
                ),
                ExpectModelProps(
                    name="array_param",
                    required=True,
                    value_type="list",
                    format=None,
                    items=[
                        ExpectModelProps(
                            name="",
                            required=True,
                            value_type="str",
                            format=Format(
                                strategy=FormatStrategy.CUSTOMIZE,
                                customize="datetime_value",
                                variables=[Variable(name="datetime_value", value_format=ValueFormat.DateTime)],
                            ),
                            items=None,
                        ),
                    ],
                ),
            ),
            (
                _adapter_config(
                    name="array_param",
                    required=True,
                    value_type="list",
                    format=None,
                    items=[
                        _adapter_config(
                            name="id",
                            required=True,
                            value_type="str",
                            format=FormatAdapter(formatter=ApiDocValueFormat.Int64),
                        ),
                        _adapter_config(
                            name="date",
                            required=True,
                            value_type="str",
                            format=FormatAdapter(formatter=ApiDocValueFormat.DateTime),
                        ),
                    ],
                ),
                ExpectModelProps(
                    name="array_param",
                    required=True,
                    value_type="list",
                    format=None,
                    items=[
                        ExpectModelProps(
                            name="id",
                            required=True,
                            value_type="str",
                            format=Format(
                                strategy=FormatStrategy.BY_DATA_TYPE,
                                size=Size(
                                    max_value=9223372036854775807,
                                    min_value=-9223372036854775808,
                                ),
                            ),
                            items=None,
                        ),
                        ExpectModelProps(
                            name="date",
                            required=True,
                            value_type="str",
                            format=Format(
                                strategy=FormatStrategy.CUSTOMIZE,
                                customize="datetime_value",
                                variables=[Variable(name="datetime_value", value_format=ValueFormat.DateTime)],
                            ),
                            items=None,
                        ),
                    ],
                ),
            ),
        ],
    )
    def test_convert_flow(
        self, adapter_model_obj, pymock_model: BaseProperty, under_test_data: dict, expect: ExpectModelProps
    ):
        adapter_model = adapter_model_obj(**under_test_data)

        serialized_data = adapter_model.serialize()
        pymock_model_has_data = pymock_model.deserialize(serialized_data)

        self._verify_data_model_props(pymock_model=pymock_model_has_data, expect=expect)

    def _verify_data_model_props(self, pymock_model: BaseProperty, expect: ExpectModelProps) -> None:
        assert pymock_model is not None
        if expect.name:
            assert pymock_model.name == expect.name
        assert pymock_model.required == expect.required
        assert pymock_model.value_type == expect.value_type
        assert pymock_model.value_format == expect.format
        if expect.items:
            assert pymock_model.items
            assert len(pymock_model.items) == len(expect.items)
            # check details of items
            for pm, e in zip(pymock_model.items, expect.items):
                self._verify_data_model_props(pymock_model=pm, expect=e)


class TestRequestParameterAdapter(_BaseTestSuite):
    @pytest.fixture(scope="function")
    def adapter_model_obj(self) -> Type[RequestParameterAdapter]:
        return RequestParameterAdapter

    @pytest.fixture(scope="function")
    def pymock_model(self) -> APIParameter:
        return APIParameter()


class TestFormatAdapter:
    @pytest.fixture(scope="function")
    def sut(self) -> FormatAdapter:
        return FormatAdapter()

    @pytest.mark.parametrize(
        ("formatter", "enum", "expected_strategy"),
        [
            (ApiDocValueFormat.Int32, [], FormatStrategy.BY_DATA_TYPE),
            (ApiDocValueFormat.Int64, [], FormatStrategy.BY_DATA_TYPE),
            (ApiDocValueFormat.Float, [], FormatStrategy.BY_DATA_TYPE),
            (ApiDocValueFormat.Double, [], FormatStrategy.BY_DATA_TYPE),
            ("", ["ENUM_1", "ENUM_2", "ENUM_3"], FormatStrategy.FROM_ENUMS),
            ("", [], None),
            (ApiDocValueFormat.Date, [], FormatStrategy.CUSTOMIZE),
            (ApiDocValueFormat.DateTime, [], FormatStrategy.CUSTOMIZE),
            (ApiDocValueFormat.EMail, [], FormatStrategy.CUSTOMIZE),
            (ApiDocValueFormat.UUID, [], FormatStrategy.CUSTOMIZE),
            (ApiDocValueFormat.URI, [], FormatStrategy.CUSTOMIZE),
            (ApiDocValueFormat.URL, [], FormatStrategy.CUSTOMIZE),
            (ApiDocValueFormat.IPv4, [], FormatStrategy.CUSTOMIZE),
            (ApiDocValueFormat.IPv6, [], FormatStrategy.CUSTOMIZE),
        ],
    )
    def test_to_pymock_api_config(
        self,
        sut: FormatAdapter,
        formatter: Optional[ApiDocValueFormat],
        enum: Optional[List[str]],
        expected_strategy: Optional[FormatStrategy],
    ):
        # given
        sut.formatter = formatter
        sut.enum = enum

        # when
        pymock_config = sut.to_pymock_api_config()

        # should
        if expected_strategy is None:
            assert pymock_config is None
        else:
            assert pymock_config.strategy and pymock_config.strategy is expected_strategy
            if pymock_config.strategy is FormatStrategy.BY_DATA_TYPE:
                if formatter in [ApiDocValueFormat.Int32, ApiDocValueFormat.Int64]:
                    assert pymock_config.size
                elif formatter in [ApiDocValueFormat.Double, ApiDocValueFormat.Float]:
                    assert pymock_config.digit

            elif pymock_config.strategy is FormatStrategy.FROM_ENUMS:
                assert pymock_config.enums
                assert pymock_config.digit is None
                assert pymock_config.size is None

            elif pymock_config.strategy is FormatStrategy.CUSTOMIZE:
                if formatter is ApiDocValueFormat.Date:
                    assert pymock_config.customize == "date_value"
                    assert pymock_config.variables
                    assert pymock_config.variables[0].name == "date_value"
                    assert pymock_config.variables[0].value_format == ValueFormat.Date
                elif formatter is ApiDocValueFormat.DateTime:
                    assert pymock_config.customize == "datetime_value"
                    assert pymock_config.variables
                    assert pymock_config.variables[0].name == "datetime_value"
                    assert pymock_config.variables[0].value_format == ValueFormat.DateTime
                elif formatter is ApiDocValueFormat.EMail:
                    assert pymock_config.customize == "email_value"
                    assert pymock_config.variables
                    assert pymock_config.variables[0].name == "email_value"
                    assert pymock_config.variables[0].value_format == ValueFormat.EMail
                elif formatter is ApiDocValueFormat.UUID:
                    assert pymock_config.customize == "uuid_value"
                    assert pymock_config.variables
                    assert pymock_config.variables[0].name == "uuid_value"
                    assert pymock_config.variables[0].value_format == ValueFormat.UUID
                elif formatter is ApiDocValueFormat.URI:
                    assert pymock_config.customize == "uri_value"
                    assert pymock_config.variables
                    assert pymock_config.variables[0].name == "uri_value"
                    assert pymock_config.variables[0].value_format == ValueFormat.URI
                elif formatter is ApiDocValueFormat.URL:
                    assert pymock_config.customize == "url_value"
                    assert pymock_config.variables
                    assert pymock_config.variables[0].name == "url_value"
                    assert pymock_config.variables[0].value_format == ValueFormat.URL
                elif formatter is ApiDocValueFormat.IPv4:
                    assert pymock_config.customize == "ipv4_value"
                    assert pymock_config.variables
                    assert pymock_config.variables[0].name == "ipv4_value"
                    assert pymock_config.variables[0].value_format == ValueFormat.IPv4
                elif formatter is ApiDocValueFormat.IPv6:
                    assert pymock_config.customize == "ipv6_value"
                    assert pymock_config.variables
                    assert pymock_config.variables[0].name == "ipv6_value"
                    assert pymock_config.variables[0].value_format == ValueFormat.IPv6

            else:
                raise NotImplementedError


class TestPropertyDetailAdapter:

    @pytest.mark.parametrize(
        ("strategy", "expected_type"),
        [
            (ResponseStrategy.OBJECT, PropertyDetailAdapter),
        ],
    )
    def test_generate_empty_response(self, strategy: ResponseStrategy, expected_type: Union[type, Type]):
        empty_resp = PropertyDetailAdapter.generate_empty_response()
        assert isinstance(empty_resp, expected_type)
