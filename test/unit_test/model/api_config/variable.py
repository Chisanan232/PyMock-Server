import re
from typing import Any, List

import pytest

from pymock_api.model.api_config.variable import Digit, Variable

from ...._values import (
    _Test_Digit_In_Format,
    _Test_Variables_BigDecimal_USD,
    _Test_Variables_Currency_Code,
)
from ._base import CheckableTestSuite, _assertion_msg, set_checking_test_data

_Digit_Test_Data: List[tuple] = []
_Variable_Test_Data: List[tuple] = []


def reset_digit_test_data() -> None:
    global _Digit_Test_Data
    _Digit_Test_Data.clear()


def add_digit_test_data(test_scenario: tuple) -> None:
    global _Digit_Test_Data
    _Digit_Test_Data.append(test_scenario)


def reset_variable_test_data() -> None:
    global _Variable_Test_Data
    _Variable_Test_Data.clear()


def add_variable_test_data(test_scenario: tuple) -> None:
    global _Variable_Test_Data
    _Variable_Test_Data.append(test_scenario)


class TestDigit(CheckableTestSuite):
    test_data_dir = "digit"
    set_checking_test_data(
        test_data_dir, reset_callback=reset_digit_test_data, opt_globals_callback=add_digit_test_data
    )

    @pytest.fixture(scope="function")
    def sut(self) -> Digit:
        return Digit(
            integer=_Test_Digit_In_Format["integer"],
            decimal=_Test_Digit_In_Format["decimal"],
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> Digit:
        return Digit()

    def test_value_attributes(self, sut: Digit):
        assert sut.integer == _Test_Digit_In_Format["integer"], _assertion_msg
        assert sut.decimal == _Test_Digit_In_Format["decimal"], _assertion_msg

    def test_serialize_with_none(self, sut_with_nothing: Digit):
        assert sut_with_nothing.serialize() is not None

    def _expected_serialize_value(self) -> Any:
        return _Test_Digit_In_Format

    def _expected_deserialize_value(self, obj: Digit) -> None:
        assert isinstance(obj, Digit)
        assert obj.integer == _Test_Digit_In_Format["integer"]
        assert obj.decimal is _Test_Digit_In_Format["decimal"]

    @pytest.mark.parametrize(
        ("test_data_path", "criteria"),
        _Digit_Test_Data,
    )
    def test_is_work(self, sut_with_nothing: Digit, test_data_path: str, criteria: bool):
        super().test_is_work(sut_with_nothing, test_data_path, criteria)


class TestVariable(CheckableTestSuite):
    test_data_dir = "variable"
    set_checking_test_data(
        test_data_dir, reset_callback=reset_variable_test_data, opt_globals_callback=add_variable_test_data
    )

    @pytest.fixture(scope="function")
    def sut(self) -> Variable:
        return Variable(
            name=_Test_Variables_BigDecimal_USD["name"],
            value_format=_Test_Variables_BigDecimal_USD["value_format"],
            digit=_Test_Variables_BigDecimal_USD["digit"],
            range=_Test_Variables_BigDecimal_USD["range"],
            enum=_Test_Variables_BigDecimal_USD["enum"],
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> Variable:
        return Variable()

    def test_value_attributes(self, sut: Variable):
        assert sut.name == _Test_Variables_BigDecimal_USD["name"], _assertion_msg
        assert sut.value_format.value is _Test_Variables_BigDecimal_USD["value_format"], _assertion_msg
        assert sut.digit.serialize() == _Test_Variables_BigDecimal_USD["digit"], _assertion_msg
        assert sut.range == _Test_Variables_BigDecimal_USD["range"], _assertion_msg
        assert sut.enum == _Test_Variables_BigDecimal_USD["enum"], _assertion_msg

    def _expected_serialize_value(self) -> Any:
        return _Test_Variables_BigDecimal_USD

    def _expected_deserialize_value(self, obj: Variable) -> None:
        assert isinstance(obj, Variable)
        assert obj.name == _Test_Variables_BigDecimal_USD["name"]
        assert obj.value_format.value is _Test_Variables_BigDecimal_USD["value_format"]
        assert obj.digit.serialize() == _Test_Variables_BigDecimal_USD["digit"]
        assert obj.range == _Test_Variables_BigDecimal_USD["range"]
        assert obj.enum == _Test_Variables_BigDecimal_USD["enum"]


class TestVariableWithEnumFormat(CheckableTestSuite):
    test_data_dir = "variable"
    set_checking_test_data(test_data_dir)

    @pytest.fixture(scope="function")
    def sut(self) -> Variable:
        return Variable(
            name=_Test_Variables_Currency_Code["name"],
            value_format=_Test_Variables_Currency_Code["value_format"],
            digit=_Test_Variables_Currency_Code["digit"],
            range=_Test_Variables_Currency_Code["range"],
            enum=_Test_Variables_Currency_Code["enum"],
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> Variable:
        return Variable()

    def test_value_attributes(self, sut: Variable):
        assert sut.name == _Test_Variables_Currency_Code["name"], _assertion_msg
        assert sut.value_format.value is _Test_Variables_Currency_Code["value_format"], _assertion_msg
        assert sut.digit == _Test_Variables_Currency_Code["digit"], _assertion_msg
        assert sut.range == _Test_Variables_Currency_Code["range"], _assertion_msg
        assert sut.enum == _Test_Variables_Currency_Code["enum"], _assertion_msg

    def _expected_serialize_value(self) -> Any:
        return _Test_Variables_Currency_Code

    def _expected_deserialize_value(self, obj: Variable) -> None:
        assert isinstance(obj, Variable)
        assert obj.name == _Test_Variables_Currency_Code["name"]
        assert obj.value_format.value is _Test_Variables_Currency_Code["value_format"]
        assert obj.digit == _Test_Variables_Currency_Code["digit"]
        assert obj.range == _Test_Variables_Currency_Code["range"]
        assert obj.enum == _Test_Variables_Currency_Code["enum"]

    @pytest.mark.parametrize(
        ("test_data_path", "criteria"),
        _Variable_Test_Data,
    )
    def test_is_work(self, sut_with_nothing: Variable, test_data_path: str, criteria: bool):
        super().test_is_work(sut_with_nothing, test_data_path, criteria)

    def test_set_with_invalid_value(self, sut_with_nothing: Variable) -> None:
        with pytest.raises(ValueError) as exc_info:
            sut_with_nothing.deserialize(data={"value_format": None})
        assert re.search(r"(.,*){0,32}value_format(.,*){0,32}cannot be empty", str(exc_info.value), re.IGNORECASE)
