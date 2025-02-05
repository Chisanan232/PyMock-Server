import logging
from typing import List, Optional, Type, Union

import pytest

from fake_api_server.model import APIParameter
from fake_api_server.model.api_config import ResponseProperty
from fake_api_server.model.api_config.apis import ResponseStrategy
from fake_api_server.model.api_config.value import FormatStrategy, ValueFormat
from fake_api_server.model.rest_api_doc_config._js_handlers import ApiDocValueFormat
from fake_api_server.model.rest_api_doc_config._model_adapter import (
    FormatAdapter,
    PropertyDetailAdapter,
    RequestParameterAdapter,
)

from ._base_config import _BasePropertyDetailAdapterTestSuite

logger = logging.getLogger(__name__)


class TestRequestParameterAdapter(_BasePropertyDetailAdapterTestSuite):
    @pytest.fixture(scope="function")
    def adapter_model_obj(self) -> Type[RequestParameterAdapter]:
        return RequestParameterAdapter

    @pytest.fixture(scope="function")
    def pyfake_model(self) -> APIParameter:
        return APIParameter()


class TestPropertyDetailAdapter(_BasePropertyDetailAdapterTestSuite):

    @pytest.mark.parametrize(
        ("strategy", "expected_type"),
        [
            (ResponseStrategy.OBJECT, PropertyDetailAdapter),
        ],
    )
    def test_generate_empty_response(self, strategy: ResponseStrategy, expected_type: Union[type, Type]):
        empty_resp = PropertyDetailAdapter.generate_empty_response()
        assert isinstance(empty_resp, expected_type)

    @pytest.fixture(scope="function")
    def adapter_model_obj(self) -> Type[PropertyDetailAdapter]:
        return PropertyDetailAdapter

    @pytest.fixture(scope="function")
    def pyfake_model(self) -> ResponseProperty:
        return ResponseProperty()


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
    def test_to_pyfake_api_config(
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
        pyfake_config = sut.to_pyfake_api_config()

        # should
        if expected_strategy is None:
            assert pyfake_config is None
        else:
            assert pyfake_config.strategy and pyfake_config.strategy is expected_strategy
            if pyfake_config.strategy is FormatStrategy.BY_DATA_TYPE:
                if formatter in [ApiDocValueFormat.Int32, ApiDocValueFormat.Int64]:
                    assert pyfake_config.size
                elif formatter in [ApiDocValueFormat.Double, ApiDocValueFormat.Float]:
                    assert pyfake_config.digit

            elif pyfake_config.strategy is FormatStrategy.FROM_ENUMS:
                assert pyfake_config.enums
                assert pyfake_config.digit is None
                assert pyfake_config.size is None

            elif pyfake_config.strategy is FormatStrategy.CUSTOMIZE:
                if formatter is ApiDocValueFormat.Date:
                    assert pyfake_config.customize == "date_value"
                    assert pyfake_config.variables
                    assert pyfake_config.variables[0].name == "date_value"
                    assert pyfake_config.variables[0].value_format == ValueFormat.Date
                elif formatter is ApiDocValueFormat.DateTime:
                    assert pyfake_config.customize == "datetime_value"
                    assert pyfake_config.variables
                    assert pyfake_config.variables[0].name == "datetime_value"
                    assert pyfake_config.variables[0].value_format == ValueFormat.DateTime
                elif formatter is ApiDocValueFormat.EMail:
                    assert pyfake_config.customize == "email_value"
                    assert pyfake_config.variables
                    assert pyfake_config.variables[0].name == "email_value"
                    assert pyfake_config.variables[0].value_format == ValueFormat.EMail
                elif formatter is ApiDocValueFormat.UUID:
                    assert pyfake_config.customize == "uuid_value"
                    assert pyfake_config.variables
                    assert pyfake_config.variables[0].name == "uuid_value"
                    assert pyfake_config.variables[0].value_format == ValueFormat.UUID
                elif formatter is ApiDocValueFormat.URI:
                    assert pyfake_config.customize == "uri_value"
                    assert pyfake_config.variables
                    assert pyfake_config.variables[0].name == "uri_value"
                    assert pyfake_config.variables[0].value_format == ValueFormat.URI
                elif formatter is ApiDocValueFormat.URL:
                    assert pyfake_config.customize == "url_value"
                    assert pyfake_config.variables
                    assert pyfake_config.variables[0].name == "url_value"
                    assert pyfake_config.variables[0].value_format == ValueFormat.URL
                elif formatter is ApiDocValueFormat.IPv4:
                    assert pyfake_config.customize == "ipv4_value"
                    assert pyfake_config.variables
                    assert pyfake_config.variables[0].name == "ipv4_value"
                    assert pyfake_config.variables[0].value_format == ValueFormat.IPv4
                elif formatter is ApiDocValueFormat.IPv6:
                    assert pyfake_config.customize == "ipv6_value"
                    assert pyfake_config.variables
                    assert pyfake_config.variables[0].name == "ipv6_value"
                    assert pyfake_config.variables[0].value_format == ValueFormat.IPv6

            else:
                raise NotImplementedError
