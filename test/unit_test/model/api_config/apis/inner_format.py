import re
from typing import Any

import pytest

from pymock_api.model.api_config.apis._format import Format

from ....._values import _Customize_Format_With_Self_Vars
from .._base import CheckableTestSuite, _assertion_msg, set_checking_test_data


class TestFormat(CheckableTestSuite):
    test_data_dir = "format"
    set_checking_test_data(test_data_dir)

    @pytest.fixture(scope="function")
    def sut(self) -> Format:
        return Format(
            strategy=_Customize_Format_With_Self_Vars["strategy"],
            enums=_Customize_Format_With_Self_Vars["enums"],
            customize=_Customize_Format_With_Self_Vars["customize"],
            variables=_Customize_Format_With_Self_Vars["variables"],
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> Format:
        return Format()

    def test_value_attributes(self, sut: Format):
        self._verify_props_value(sut)

    def _expected_serialize_value(self) -> Any:
        return _Customize_Format_With_Self_Vars

    def _expected_deserialize_value(self, obj: Format) -> None:
        assert isinstance(obj, Format)
        self._verify_props_value(ut_obj=obj)

    def _verify_props_value(self, ut_obj: Format) -> None:
        assert ut_obj.strategy.value == _Customize_Format_With_Self_Vars["strategy"], _assertion_msg
        assert ut_obj.enums is _Customize_Format_With_Self_Vars["enums"], _assertion_msg
        assert ut_obj.customize is _Customize_Format_With_Self_Vars["customize"], _assertion_msg
        for var in ut_obj.variables:
            expect_var_value = list(
                filter(lambda v: v["name"] == var.name, _Customize_Format_With_Self_Vars["variables"])
            )
            assert expect_var_value and len(expect_var_value) == 1
            assert var.name == expect_var_value[0]["name"]
            assert var.value_format.value == expect_var_value[0]["value_format"]
            assert var.value == expect_var_value[0]["value"]
            assert var.range == expect_var_value[0]["range"]
            assert var.enum == expect_var_value[0]["enum"]

    @pytest.mark.parametrize("invalid_data", ["invalid data type", ["invalid data type"]])
    def test_invalid_data_at_prop_variables(self, invalid_data: Any):
        with pytest.raises(TypeError) as exc_info:
            Format(variables=invalid_data)
        assert re.search(
            r".{0,32}data type(.,*){0,32}variables(.,*){0,32}be(.,'){0,32}", str(exc_info.value), re.IGNORECASE
        )

    def test_set_with_invalid_value(self, sut_with_nothing: Format):
        with pytest.raises(ValueError) as exc_info:
            sut_with_nothing.deserialize(data={"strategy": None})
        assert re.search(r"(.,*){0,32}strategy(.,*){0,32}cannot be empty", str(exc_info.value), re.IGNORECASE)
