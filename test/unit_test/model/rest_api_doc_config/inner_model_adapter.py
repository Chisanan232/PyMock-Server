from typing import List, Optional, Type, Union

import pytest

from pymock_server.model.api_config.apis import ResponseStrategy
from pymock_server.model.api_config.value import FormatStrategy, ValueFormat
from pymock_server.model.rest_api_doc_config._js_handlers import ApiDocValueFormat
from pymock_server.model.rest_api_doc_config._model_adapter import (
    FormatAdapter,
    PropertyDetailAdapter,
)


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
            (ApiDocValueFormat.Date, [], FormatStrategy.BY_DATA_TYPE),
            (ApiDocValueFormat.DateTime, [], FormatStrategy.BY_DATA_TYPE),
            (ApiDocValueFormat.EMail, [], FormatStrategy.BY_DATA_TYPE),
            (ApiDocValueFormat.UUID, [], FormatStrategy.BY_DATA_TYPE),
            (ApiDocValueFormat.URI, [], FormatStrategy.BY_DATA_TYPE),
            (ApiDocValueFormat.URL, [], FormatStrategy.BY_DATA_TYPE),
            (ApiDocValueFormat.IPv4, [], FormatStrategy.BY_DATA_TYPE),
            (ApiDocValueFormat.IPv6, [], FormatStrategy.BY_DATA_TYPE),
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
                elif formatter in [ApiDocValueFormat.Int32, ApiDocValueFormat.Int64]:
                    assert pymock_config.size
                elif formatter in [ApiDocValueFormat.Double, ApiDocValueFormat.Float]:
                    assert pymock_config.digit

            elif pymock_config.strategy is FormatStrategy.FROM_ENUMS:
                assert pymock_config.enums
                assert pymock_config.digit is None
                assert pymock_config.size is None
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
