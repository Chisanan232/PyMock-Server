import re
from typing import Any, Type

import pytest

from pymock_server.model.api_config.template._load.key import (
    ConfigLoadingOrder,
    set_loading_function,
)

from ...._enums import EnumTestSuite


def test_set_loading_function():
    with pytest.raises(KeyError) as exc_info:
        set_loading_function(data_model_key="data_model", invalid_arg="any value")
    assert re.search(
        r"The arguments only have \*apis\*, \*file\* and \*apply\*.{0,64}", str(exc_info.value), re.IGNORECASE
    )


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
