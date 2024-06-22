from typing import Any

import pytest

from pymock_api.model.api_config.variables import Variable

from ...._values import _Test_Variables_BigDecimal_USD
from ._base import CheckableTestSuite, _assertion_msg, set_checking_test_data


class TestVariable(CheckableTestSuite):
    test_data_dir = "variables"
    set_checking_test_data(test_data_dir)

    @pytest.fixture(scope="function")
    def sut(self) -> Variable:
        return Variable(
            name=_Test_Variables_BigDecimal_USD["name"],
            value_format=_Test_Variables_BigDecimal_USD["value_format"],
            value=_Test_Variables_BigDecimal_USD["value"],
            range=_Test_Variables_BigDecimal_USD["range"],
            enum=_Test_Variables_BigDecimal_USD["enum"],
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> Variable:
        return Variable()

    def test_value_attributes(self, sut: Variable):
        assert sut.name == _Test_Variables_BigDecimal_USD["name"], _assertion_msg
        assert sut.value_format.value is _Test_Variables_BigDecimal_USD["value_format"], _assertion_msg
        assert sut.value == _Test_Variables_BigDecimal_USD["value"], _assertion_msg
        assert sut.range == _Test_Variables_BigDecimal_USD["range"], _assertion_msg
        assert sut.enum == _Test_Variables_BigDecimal_USD["enum"], _assertion_msg

    def _expected_serialize_value(self) -> Any:
        return _Test_Variables_BigDecimal_USD

    def _expected_deserialize_value(self, obj: Variable) -> None:
        assert isinstance(obj, Variable)
        assert obj.name == _Test_Variables_BigDecimal_USD["name"]
        assert obj.value_format.value is _Test_Variables_BigDecimal_USD["value_format"]
        assert obj.value == _Test_Variables_BigDecimal_USD["value"]
        assert obj.range == _Test_Variables_BigDecimal_USD["range"]
        assert obj.enum == _Test_Variables_BigDecimal_USD["enum"]
