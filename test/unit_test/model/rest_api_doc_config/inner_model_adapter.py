from typing import List, Optional, Type, Union

import pytest

from pymock_server.model.api_config.apis import ResponseStrategy
from pymock_server.model.api_config.value import FormatStrategy
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
            ("date-time", [], FormatStrategy.BY_DATA_TYPE),
            ("int32", [], FormatStrategy.BY_DATA_TYPE),
            ("int64", [], FormatStrategy.BY_DATA_TYPE),
            ("", ["ENUM_1", "ENUM_2", "ENUM_3"], FormatStrategy.FROM_ENUMS),
            ("", [], None),
        ],
    )
    def test_to_pymock_api_config(
        self,
        sut: FormatAdapter,
        formatter: Optional[str],
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
                assert pymock_config
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
