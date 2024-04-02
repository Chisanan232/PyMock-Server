import re
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Any, Type

import pytest

from pymock_api.model.enums import (
    ConfigLoadingOrder,
    OpenAPIVersion,
    ResponseStrategy,
    set_loading_function,
)


def test_set_loading_function():
    with pytest.raises(KeyError) as exc_info:
        set_loading_function(data_model_key="data_model", invalid_arg="any value")
    assert re.search(
        r"The arguments only have \*apis\*, \*file\* and \*apply\*.{0,64}", str(exc_info.value), re.IGNORECASE
    )


class EnumTestSuite(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def enum_obj(self) -> Type[Enum]:
        pass

    def test_to_enum(self, value: Any, enum_obj: Type[Enum]):
        result = enum_obj.to_enum(value)
        assert isinstance(result, enum_obj)


class TestResponseStrategy(EnumTestSuite):
    @pytest.fixture(scope="function")
    def enum_obj(self) -> Type[ResponseStrategy]:
        return ResponseStrategy

    @pytest.mark.parametrize(
        "value",
        [
            ResponseStrategy.STRING,
            ResponseStrategy.FILE,
            "string",
            "object",
        ],
    )
    def test_to_enum(self, value: Any, enum_obj: Type[ResponseStrategy]):
        super().test_to_enum(value, enum_obj)


class TestConfigLoadingOrder(EnumTestSuite):
    @pytest.fixture(scope="function")
    def enum_obj(self) -> Type[ConfigLoadingOrder]:
        return ConfigLoadingOrder

    @pytest.mark.parametrize(
        "value",
        [
            ConfigLoadingOrder.APIs,
            ConfigLoadingOrder.APPLY,
            "apis",
            "file",
        ],
    )
    def test_to_enum(self, value: Any, enum_obj: Type[ConfigLoadingOrder]):
        super().test_to_enum(value, enum_obj)


class TestOpenAPIVersion(EnumTestSuite):
    @pytest.fixture(scope="function")
    def enum_obj(self) -> Type[OpenAPIVersion]:
        return OpenAPIVersion

    @pytest.mark.parametrize(
        "value",
        [
            OpenAPIVersion.V2,
            OpenAPIVersion.V3,
            "OpenAPI V2",
            "OpenAPI V3",
            "2.0",
            "2.0.0",
            "2.0.4",
            "2.3.7",
            "3.0",
            "3.0.0",
            "3.0.9",
            "3.1.0",
        ],
    )
    def test_to_enum(self, value: Any, enum_obj: Type[OpenAPIVersion]):
        super().test_to_enum(value, enum_obj)

    @pytest.mark.parametrize("value", ["1.0.0", "4.0.0", "invalid value"])
    def test_invalid_enum(self, enum_obj: Type[OpenAPIVersion], value: str):
        with pytest.raises(NotImplementedError) as exc_info:
            enum_obj.to_enum(value)
        assert re.search(re.escape(value), str(exc_info.value)) is not None
