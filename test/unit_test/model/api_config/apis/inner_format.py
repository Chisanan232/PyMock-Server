import copy
import re
from decimal import Decimal
from typing import Any, List, Optional, Union

import pytest

from pymock_api._utils.random import ValueSize
from pymock_api.model import TemplateConfig
from pymock_api.model.api_config.format import Format
from pymock_api.model.api_config.template import TemplateCommonConfig
from pymock_api.model.api_config.template.common import (
    TemplateFormatConfig,
    TemplateFormatEntity,
)
from pymock_api.model.api_config.variable import Digit, Size, Variable
from pymock_api.model.enums import FormatStrategy, ValueFormat

from ....._test_utils import Verify
from ....._values import _Customize_Format_With_Self_Vars, _General_Format
from .._base import (
    CheckableTestSuite,
    ConfigTestSpec,
    _assertion_msg,
    set_checking_test_data,
)


class TestFormatWithGeneralStrategy(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> Format:
        return Format(
            strategy=_General_Format["strategy"],
            digit=_General_Format["digit"],
            size=_General_Format["size"],
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> Format:
        return Format()

    def test_value_attributes(self, sut: Format):
        self._verify_props_value(sut, self._expected_serialize_value())

    def _expected_serialize_value(self) -> dict:
        return _General_Format

    def _expected_deserialize_value(self, obj: Format) -> None:
        assert isinstance(obj, Format)
        self._verify_props_value(ut_obj=obj, expect_format=self._expected_serialize_value())

    def _verify_props_value(self, ut_obj: Format, expect_format: dict) -> None:
        assert ut_obj.strategy.value == expect_format["strategy"], _assertion_msg
        if expect_format.get("digit", None):
            assert ut_obj.digit.serialize() == expect_format.get("digit", None), _assertion_msg
        if expect_format.get("size", None):
            assert ut_obj.size.serialize() == expect_format.get("size", None), _assertion_msg
        assert ut_obj.enums == expect_format.get("enums", []), _assertion_msg
        assert ut_obj.customize == expect_format.get("customize", ""), _assertion_msg
        for var in ut_obj.variables:
            expect_var_value = list(filter(lambda v: v["name"] == var.name, expect_format["variables"]))
            assert expect_var_value and len(expect_var_value) == 1
            assert var.name == expect_var_value[0]["name"]
            assert var.value_format.value == expect_var_value[0]["value_format"]
            if expect_var_value[0]["digit"]:
                assert var.digit.integer == expect_var_value[0]["digit"]["integer"]
                assert var.digit.decimal == expect_var_value[0]["digit"]["decimal"]
            if expect_var_value[0]["size"]:
                assert var.size.max_value == expect_var_value[0]["size"]["max"]
                assert var.size.min_value == expect_var_value[0]["size"]["min"]
            assert var.enum == expect_var_value[0]["enum"]


class TestFormatWithCustomizeStrategy(TestFormatWithGeneralStrategy, CheckableTestSuite):
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

    def _expected_serialize_value(self) -> Any:
        return _Customize_Format_With_Self_Vars

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

    @pytest.mark.parametrize(
        ("ut_obj", "other_obj"),
        [
            (Format(strategy=FormatStrategy.BY_DATA_TYPE), Format(strategy=FormatStrategy.CUSTOMIZE)),
            (
                Format(strategy=FormatStrategy.FROM_ENUMS, enums=["ENUM_1", "ENUM_2"]),
                Format(strategy=FormatStrategy.FROM_ENUMS, enums=["ENUM_3"]),
            ),
            (
                Format(strategy=FormatStrategy.CUSTOMIZE, customize="sample customize"),
                Format(strategy=FormatStrategy.CUSTOMIZE, customize="different customize"),
            ),
            (
                Format(
                    strategy=FormatStrategy.CUSTOMIZE,
                    customize="customize with var",
                    variables=[Variable(name="sample var")],
                ),
                Format(
                    strategy=FormatStrategy.CUSTOMIZE,
                    customize="customize with var",
                    variables=[Variable(name="different var name")],
                ),
            ),
            (
                Format(
                    strategy=FormatStrategy.CUSTOMIZE,
                    customize="customize with var",
                    variables=[Variable(name="sample var", digit=Digit(integer=20))],
                ),
                Format(
                    strategy=FormatStrategy.CUSTOMIZE,
                    customize="customize with var",
                    variables=[Variable(name="sample var", digit=Digit(integer=30, decimal=2))],
                ),
            ),
        ],
    )
    def test_compare(self, ut_obj: Format, other_obj: Format):
        assert ut_obj != other_obj

    @pytest.mark.parametrize(
        ("strategy", "data_type", "value", "digit", "enums", "customize", "variables"),
        [
            (FormatStrategy.BY_DATA_TYPE, str, "random_string", None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, str, "123", None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, str, "@\-_!#$%^&+*()\[\]<>?=/\\|`'\"}{~:;,.", None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, int, 123, None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, int, 123, Digit(integer=3, decimal=0), [], "", []),
            (FormatStrategy.BY_DATA_TYPE, int, 123, Digit(integer=5, decimal=2), [], "", []),
            (FormatStrategy.BY_DATA_TYPE, "big_decimal", 123.123, None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, "big_decimal", 123.123, Digit(integer=3, decimal=3), [], "", []),
            (FormatStrategy.BY_DATA_TYPE, "big_decimal", 123.123, Digit(integer=5, decimal=4), [], "", []),
            (FormatStrategy.BY_DATA_TYPE, bool, True, None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, bool, False, None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, bool, "True", None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, bool, "False", None, [], "", []),
            (FormatStrategy.FROM_ENUMS, str, "ENUM_2", None, ["ENUM_1", "ENUM_2", "ENUM_3"], "", []),
            (FormatStrategy.CUSTOMIZE, str, "sample_format", None, [], "sample_format", []),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "sample_format",
                None,
                [],
                "<string_check>",
                [Variable(name="string_check", value_format=ValueFormat.String)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "true",
                None,
                [],
                "<boolean_check>",
                [Variable(name="boolean_check", value_format=ValueFormat.Boolean)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "ENUM_3",
                None,
                [],
                "<enum_check>",
                [
                    Variable(
                        name="enum_check",
                        value_format=ValueFormat.Enum,
                        enum=["ENUM_1", "ENUM_2", "ENUM_3", "ENUM_4", "ENUM_5"],
                    )
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "123.123 USD",
                None,
                [],
                "<decimal_price> <fiat_currency_code>",
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "123.123 USD",
                None,
                [],
                "<decimal_price_with_digit> <fiat_currency_code>",
                [
                    Variable(
                        name="decimal_price_with_digit",
                        value_format=ValueFormat.BigDecimal,
                        digit=Digit(integer=3, decimal=3),
                    ),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "123.123 USD\n 135789 JPY",
                None,
                [],
                "<decimal_price> <fiat_currency_code>\n <decimal_price> <fiat_currency_code>",
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "123.123 USD\n 135789 JPY",
                None,
                [],
                "<decimal_price_with_digit> <fiat_currency_code>\n <decimal_price_with_digit> <fiat_currency_code>",
                [
                    Variable(
                        name="decimal_price_with_digit",
                        value_format=ValueFormat.BigDecimal,
                        digit=Digit(integer=10, decimal=4),
                    ),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "123.123 USD\n 135789 JPY\n the lowest value",
                None,
                [],
                "<decimal_price> <fiat_currency_code>\n <decimal_price> <fiat_currency_code>\n <string_value>",
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                    Variable(name="string_value", value_format=ValueFormat.String),
                ],
            ),
        ],
    )
    def test_chk_format_is_match(
        self,
        strategy: FormatStrategy,
        data_type: Union[str, object],
        value: Any,
        digit: Optional[Digit],
        enums: List[str],
        customize: str,
        variables: List[Variable],
    ):
        format_model = Format(
            strategy=strategy,
            size=Size(max_value=64, min_value=0),
            digit=digit,
            enums=enums,
            customize=customize,
            variables=variables,
        )
        assert format_model.value_format_is_match(data_type=data_type, value=value) is True

    @pytest.mark.parametrize(
        ("strategy", "use_name", "data_type", "value", "customize", "variables_in_format", "variables_in_template"),
        [
            # *CUSTOMIZE* with template variables
            (FormatStrategy.CUSTOMIZE, "", str, "sample_format", "sample_format", [], []),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "sample_format",
                "<string_check>",
                [],
                [Variable(name="string_check", value_format=ValueFormat.String)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "true",
                "<boolean_check>",
                [],
                [Variable(name="boolean_check", value_format=ValueFormat.Boolean)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "ENUM_3",
                "<enum_check>",
                [],
                [
                    Variable(
                        name="enum_check",
                        value_format=ValueFormat.Enum,
                        enum=["ENUM_1", "ENUM_2", "ENUM_3", "ENUM_4", "ENUM_5"],
                    )
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "123.123 USD",
                "<decimal_price> <fiat_currency_code>",
                [],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "123.123 USD",
                "<decimal_price_with_digit> <fiat_currency_code>",
                [],
                [
                    Variable(
                        name="decimal_price_with_digit",
                        value_format=ValueFormat.BigDecimal,
                        digit=Digit(integer=3, decimal=3),
                    ),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "123.123 USD\n 135789 JPY",
                "<decimal_price> <fiat_currency_code>\n <decimal_price> <fiat_currency_code>",
                [],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "123.123 USD\n 135789 JPY",
                "<decimal_price_with_digit> <fiat_currency_code>\n <decimal_price_with_digit> <fiat_currency_code>",
                [],
                [
                    Variable(
                        name="decimal_price_with_digit",
                        value_format=ValueFormat.BigDecimal,
                        digit=Digit(integer=10, decimal=4),
                    ),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "123.123 USD\n 135789 JPY\n the lowest value",
                "<decimal_price> <fiat_currency_code>\n <decimal_price> <fiat_currency_code>\n <string_value>",
                [],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                    Variable(name="string_value", value_format=ValueFormat.String),
                ],
            ),
            # *CUSTOMIZE* with template variables and override variable settings
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "ENUM_2",
                "<boolean_check>",
                [
                    Variable(
                        name="boolean_check",
                        value_format=ValueFormat.Enum,
                        enum=["ENUM_1", "ENUM_2", "ENUM_3", "ENUM_4", "ENUM_5"],
                    ),
                ],
                [Variable(name="boolean_check", value_format=ValueFormat.Boolean)],
            ),
            # *FROM_TEMPLATE* with template variables
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_str_format",
                str,
                "sample_format",
                "<string_check>",
                [],
                [Variable(name="string_check", value_format=ValueFormat.String)],
            ),
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_bool_format",
                str,
                "true",
                "<boolean_check>",
                [],
                [Variable(name="boolean_check", value_format=ValueFormat.Boolean)],
            ),
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_enum_format",
                str,
                "ENUM_3",
                "<enum_check>",
                [],
                [
                    Variable(
                        name="enum_check",
                        value_format=ValueFormat.Enum,
                        enum=["ENUM_1", "ENUM_2", "ENUM_3", "ENUM_4", "ENUM_5"],
                    )
                ],
            ),
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_customize_format",
                str,
                "123.123 USD",
                "<decimal_price> <fiat_currency_code>",
                [],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_customize_format",
                str,
                "123.123 USD",
                "<decimal_price_with_digit> <fiat_currency_code>",
                [],
                [
                    Variable(
                        name="decimal_price_with_digit",
                        value_format=ValueFormat.BigDecimal,
                        digit=Digit(integer=3, decimal=3),
                    ),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_customize_format",
                str,
                "123.123 USD\n 135789 JPY",
                "<decimal_price> <fiat_currency_code>\n <decimal_price> <fiat_currency_code>",
                [],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_customize_format",
                str,
                "123.123 USD\n 135789 JPY",
                "<decimal_price_with_digit> <fiat_currency_code>\n <decimal_price_with_digit> <fiat_currency_code>",
                [],
                [
                    Variable(
                        name="decimal_price_with_digit",
                        value_format=ValueFormat.BigDecimal,
                        digit=Digit(integer=10, decimal=4),
                    ),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_customize_format",
                str,
                "123.123 USD\n 135789 JPY\n the lowest value",
                "<decimal_price> <fiat_currency_code>\n <decimal_price> <fiat_currency_code>\n <string_value>",
                [],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                    Variable(name="string_value", value_format=ValueFormat.String),
                ],
            ),
            # *FROM_TEMPLATE* with partial template variables
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_customize_format",
                str,
                "123.123 USD\n 135789 JPY\n the lowest value",
                "<decimal_price> <fiat_currency_code>\n <decimal_price> <fiat_currency_code>\n <string_value>",
                [
                    Variable(name="string_value", value_format=ValueFormat.String),
                ],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
        ],
    )
    def test_chk_format_is_match_with_template_config(
        self,
        strategy: FormatStrategy,
        use_name: str,
        data_type: Union[str, object],
        value: Any,
        customize: str,
        variables_in_format: List[Variable],
        variables_in_template: List[Variable],
    ):
        format_model = self._given_template_format_setting(
            customize=customize,
            strategy=strategy,
            use_name=use_name,
            variables_in_template=variables_in_template,
            variables_in_format=variables_in_format,
        )

        assert format_model.value_format_is_match(data_type=data_type, value=value) is True

    @pytest.mark.parametrize(
        ("strategy", "data_type", "value", "digit", "enums", "customize", "variables"),
        [
            (FormatStrategy.BY_DATA_TYPE, str, "".join(["a" for _ in range(6)]), None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, int, "not int value", None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, int, 123, Digit(integer=1, decimal=0), [], "", []),
            (FormatStrategy.BY_DATA_TYPE, "big_decimal", "not int or float value", None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, "big_decimal", 123.123, Digit(integer=2, decimal=3), [], "", []),
            (FormatStrategy.BY_DATA_TYPE, "big_decimal", 123.123, Digit(integer=3, decimal=1), [], "", []),
            (FormatStrategy.BY_DATA_TYPE, bool, "not bool value", None, [], "", []),
            (FormatStrategy.FROM_ENUMS, str, "not in enums", None, ["ENUM_1", "ENUM_2", "ENUM_3"], "", []),
            (FormatStrategy.CUSTOMIZE, str, "different_format", None, [], "sample_format", []),
            (
                FormatStrategy.CUSTOMIZE,
                int,
                "not integer",
                None,
                [],
                "<integer_check>",
                [Variable(name="integer_check", value_format=ValueFormat.Integer)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                bool,
                "not boolean",
                None,
                [],
                "<boolean_check>",
                [Variable(name="boolean_check", value_format=ValueFormat.Boolean)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "ENUM_NOT_EXIST",
                None,
                [],
                "<enum_check>",
                [
                    Variable(
                        name="enum_check",
                        value_format=ValueFormat.Enum,
                        enum=["ENUM_1", "ENUM_2", "ENUM_3", "ENUM_4", "ENUM_5"],
                    )
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "123.123 EUR",
                None,
                [],
                "<decimal_price> <fiat_currency_code>",
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "123.123 USD\n 135789 JPY",
                None,
                [],
                "<decimal_price> <fiat_currency_code> <decimal_price> <fiat_currency_code>",
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "123.123 USD\n incorrect_value JPY\n the lowest value",
                None,
                [],
                "<decimal_price> <fiat_currency_code>\n <decimal_price> <fiat_currency_code>\n <string_value>",
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                    Variable(name="string_value", value_format=ValueFormat.String),
                ],
            ),
        ],
    )
    def test_failure_chk_format_is_match(
        self,
        strategy: FormatStrategy,
        data_type: Union[str, object],
        value: Any,
        digit: Optional[Digit],
        enums: List[str],
        customize: str,
        variables: List[Variable],
    ):
        format_model = Format(
            strategy=strategy,
            size=Size(max_value=5, min_value=0),
            digit=digit,
            enums=enums,
            customize=customize,
            variables=variables,
        )
        assert format_model.value_format_is_match(data_type=data_type, value=value) is False

    @pytest.mark.parametrize(
        ("strategy", "use_name", "data_type", "value", "customize", "variables_in_format", "variables_in_template"),
        [
            # *CUSTOMIZE* with template variables
            (FormatStrategy.CUSTOMIZE, "", str, "different_format", "sample_format", [], []),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                int,
                "not integer",
                "<integer_check>",
                [],
                [Variable(name="integer_check", value_format=ValueFormat.Integer)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                bool,
                "not boolean",
                "<boolean_check>",
                [],
                [Variable(name="boolean_check", value_format=ValueFormat.Boolean)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "ENUM_NOT_EXIST",
                "<enum_check>",
                [],
                [
                    Variable(
                        name="enum_check",
                        value_format=ValueFormat.Enum,
                        enum=["ENUM_1", "ENUM_2", "ENUM_3", "ENUM_4", "ENUM_5"],
                    )
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "123.123 EUR",
                "<decimal_price> <fiat_currency_code>",
                [],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "123.123 USD\n 135789 JPY",
                "<decimal_price> <fiat_currency_code> <decimal_price> <fiat_currency_code>",
                [],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "123.123 USD\n incorrect_value JPY\n the lowest value",
                "<decimal_price> <fiat_currency_code>\n <decimal_price> <fiat_currency_code>\n <string_value>",
                [],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                    Variable(name="string_value", value_format=ValueFormat.String),
                ],
            ),
            # *CUSTOMIZE* with template variables and override variable settings
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "ENUM_2",
                "<boolean_check>",
                [Variable(name="boolean_check", value_format=ValueFormat.Boolean)],
                [
                    Variable(
                        name="boolean_check",
                        value_format=ValueFormat.Enum,
                        enum=["ENUM_1", "ENUM_2", "ENUM_3", "ENUM_4", "ENUM_5"],
                    ),
                ],
            ),
            # *FROM_TEMPLATE* with template variables
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_str_format",
                str,
                "sample_format",
                "<string_check>",
                [],
                [Variable(name="string_check", value_format=ValueFormat.Boolean)],
            ),
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_bool_format",
                str,
                "true",
                "<boolean_check>",
                [],
                [Variable(name="boolean_check", value_format=ValueFormat.Integer)],
            ),
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_enum_format",
                str,
                "ENUM_NOT_EXIST",
                "<enum_check>",
                [],
                [
                    Variable(
                        name="enum_check",
                        value_format=ValueFormat.Enum,
                        enum=["ENUM_1", "ENUM_2", "ENUM_3", "ENUM_4", "ENUM_5"],
                    )
                ],
            ),
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_customize_format",
                str,
                "123.123 EUR",
                "<decimal_price> <fiat_currency_code>",
                [],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.Integer),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            # *FROM_TEMPLATE* with partial template variables
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_customize_format",
                str,
                "123.123 USD\n 135789 EUR\n the lowest value",
                "<decimal_price> <fiat_currency_code>\n <decimal_price> <fiat_currency_code>\n <string_value>",
                [
                    Variable(name="string_value", value_format=ValueFormat.String),
                ],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
        ],
    )
    def test_failure_chk_format_is_match_with_template_config(
        self,
        strategy: FormatStrategy,
        use_name: str,
        data_type: Union[str, object],
        value: Any,
        customize: str,
        variables_in_format: List[Variable],
        variables_in_template: List[Variable],
    ):
        format_model = self._given_template_format_setting(
            customize=customize,
            strategy=strategy,
            use_name=use_name,
            variables_in_template=variables_in_template,
            variables_in_format=variables_in_format,
        )

        assert format_model.value_format_is_match(data_type=data_type, value=value) is False

    def _given_template_format_setting(
        self,
        strategy: FormatStrategy,
        use_name: str,
        customize: str,
        variables_in_format: List[Variable],
        variables_in_template: List[Variable],
    ) -> Format:
        # Given under test format
        format_model = Format(
            strategy=strategy,
            size=Size(max_value=64, min_value=0),
            customize=customize if strategy is FormatStrategy.CUSTOMIZE else "",
            variables=variables_in_format,
            use_name=use_name,
        )

        # Given the format instance will be saved in *template.common_config.format.entities*
        format_model_in_template = copy.copy(format_model)
        format_model_in_template.strategy = FormatStrategy.CUSTOMIZE
        format_model_in_template.customize = customize

        # Given the template configuration
        format_model._current_template = TemplateConfig(
            activate=True,
            common_config=TemplateCommonConfig(
                activate=True,
                format=TemplateFormatConfig(
                    entities=[TemplateFormatEntity(name=use_name, config=format_model_in_template)],
                    variables=variables_in_template,
                ),
            ),
        )
        return format_model

    @pytest.mark.parametrize(
        ("strategy", "data_type", "enums", "customize", "expect_type", "expect_value_format"),
        [
            (FormatStrategy.BY_DATA_TYPE, str, [], "", str, None),
            (FormatStrategy.BY_DATA_TYPE, int, [], "", int, None),
            (FormatStrategy.BY_DATA_TYPE, "big_decimal", [], "", Decimal, None),
            (FormatStrategy.BY_DATA_TYPE, bool, [], "", bool, None),
            (FormatStrategy.FROM_ENUMS, str, ["ENUM_1", "ENUM_2", "ENUM_3"], "", str, None),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                [],
                "<big_decimal_price> <fiat_currency_code>",
                str,
                r"\d{0,64}(\.)\d{0,64} \w{0,10}",
            ),
        ],
    )
    def test_generate_value(
        self,
        strategy: FormatStrategy,
        data_type: Union[None, str, object],
        enums: List[str],
        customize: str,
        expect_type: type,
        expect_value_format: Optional[str],
    ):
        format_model = Format(
            strategy=strategy,
            enums=enums,
            customize=customize,
            variables=[
                Variable(
                    name="big_decimal_price", value_format=ValueFormat.BigDecimal, digit=Digit(), size=Size(), enum=[]
                ),
                Variable(
                    name="fiat_currency_code",
                    value_format=ValueFormat.Enum,
                    digit=Digit(),
                    size=Size(),
                    enum=["USD", "TWD"],
                ),
            ],
        )
        value = format_model.generate_value(data_type=data_type)
        assert value is not None
        assert isinstance(value, expect_type)
        if enums:
            assert value in enums
        if expect_value_format:
            assert re.search(expect_value_format, str(value), re.IGNORECASE) is not None

    @pytest.mark.parametrize(
        ("strategy", "data_type", "size"),
        [
            (FormatStrategy.BY_DATA_TYPE, str, Size(max_value=3, min_value=0)),
            (FormatStrategy.BY_DATA_TYPE, str, Size(max_value=10, min_value=6)),
        ],
    )
    def test_generate_string_value(self, strategy: FormatStrategy, data_type: object, size: Size):
        format_data_model = Format(strategy=strategy, size=size)
        value = format_data_model.generate_value(data_type=data_type)
        assert isinstance(value, data_type)
        assert size.min_value <= len(value) <= size.max_value

    @pytest.mark.parametrize(
        ("strategy", "data_type", "digit", "expect_type", "expect_value_range"),
        [
            (FormatStrategy.BY_DATA_TYPE, int, Digit(integer=1, decimal=0), int, ValueSize(min=-9, max=9)),
            (FormatStrategy.BY_DATA_TYPE, int, Digit(integer=3, decimal=0), int, ValueSize(min=-999, max=999)),
            (FormatStrategy.BY_DATA_TYPE, int, Digit(integer=1, decimal=2), int, ValueSize(min=-9, max=9)),
            (FormatStrategy.BY_DATA_TYPE, float, Digit(integer=1, decimal=0), Decimal, ValueSize(min=-9, max=9)),
            (
                FormatStrategy.BY_DATA_TYPE,
                float,
                Digit(integer=3, decimal=0),
                Decimal,
                ValueSize(min=-999, max=999),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                float,
                Digit(integer=3, decimal=2),
                Decimal,
                ValueSize(min=-999.99, max=999.99),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                float,
                Digit(integer=0, decimal=3),
                Decimal,
                ValueSize(min=-0.999, max=0.999),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                "big_decimal",
                Digit(integer=1, decimal=0),
                Decimal,
                ValueSize(min=-9, max=9),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                "big_decimal",
                Digit(integer=3, decimal=0),
                Decimal,
                ValueSize(min=-999, max=999),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                "big_decimal",
                Digit(integer=3, decimal=2),
                Decimal,
                ValueSize(min=-999.99, max=999.99),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                "big_decimal",
                Digit(integer=0, decimal=3),
                Decimal,
                ValueSize(min=-0.999, max=0.999),
            ),
        ],
    )
    def test_generate_numerical_value(
        self,
        strategy: FormatStrategy,
        data_type: Union[None, str, object],
        digit: Digit,
        expect_type: type,
        expect_value_range: ValueSize,
    ):
        format_model = Format(
            strategy=strategy,
            digit=digit,
        )
        value = format_model.generate_value(data_type=data_type)
        assert value is not None
        assert isinstance(value, expect_type)
        Verify.numerical_value_should_be_in_range(value=value, expect_range=expect_value_range)

    def test_invalid_expect_format_log_msg(self):
        non_strategy_format = Format(strategy=None)
        with pytest.raises(ValueError):
            non_strategy_format.expect_format_log_msg(data_type="any data type")
