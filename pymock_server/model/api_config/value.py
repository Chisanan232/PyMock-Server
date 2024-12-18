import re
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Union

from pymock_server._utils.random import (
    DigitRange,
    RandomBigDecimal,
    RandomBoolean,
    RandomFromSequence,
    RandomInteger,
    RandomString,
    ValueSize,
)

Default_Value_Size = ValueSize(max=10, min=1)
Default_Digit_Range = DigitRange(integer=128, decimal=128)


class ValueFormat(Enum):
    String: str = "str"
    Integer: str = "int"
    BigDecimal: str = "big_decimal"
    Boolean: str = "bool"
    Enum: str = "enum"

    @staticmethod
    def to_enum(v: Union[str, type, "ValueFormat"]) -> "ValueFormat":
        if isinstance(v, str):
            return ValueFormat(v.lower())
        elif isinstance(v, type):
            if v is str:
                return ValueFormat.String
            elif v is int:
                return ValueFormat.Integer
            elif v is float:
                return ValueFormat.BigDecimal
            elif v is bool:
                return ValueFormat.Boolean
            else:
                raise ValueError(f"For the native data type, it doesn't support {v} recently.")
        else:
            return v

    def generate_value(
        self, enums: List[str] = [], size: ValueSize = Default_Value_Size, digit: DigitRange = Default_Digit_Range
    ) -> Union[str, int, bool, Decimal]:

        def _generate_max_value(digit_number: int) -> int:
            return int("".join(["9" for _ in range(digit_number)])) if digit_number > 0 else 0

        self._ensure_setting_value_is_valid(enums=enums, size=size, digit=digit)
        if self is ValueFormat.String:
            return RandomString.generate(size=size)
        elif self is ValueFormat.Integer:
            max_value = _generate_max_value(digit.integer)
            return RandomInteger.generate(value_range=ValueSize(min=0 - max_value, max=max_value))
        elif self is ValueFormat.BigDecimal:
            max_integer_value = _generate_max_value(digit.integer)
            max_decimal_value = _generate_max_value(digit.decimal)
            return RandomBigDecimal.generate(
                integer_range=ValueSize(min=0 - max_integer_value, max=max_integer_value),
                decimal_range=ValueSize(min=0, max=max_decimal_value),
            )
        elif self is ValueFormat.Boolean:
            return RandomBoolean.generate()
        elif self is ValueFormat.Enum:
            return RandomFromSequence.generate(enums)
        else:
            raise NotImplementedError(f"Doesn't implement how to generate the value by format {self}.")

    def generate_regex(
        self, enums: List[str] = [], size: ValueSize = Default_Value_Size, digit: DigitRange = Default_Digit_Range
    ) -> str:
        self._ensure_setting_value_is_valid(enums=enums, size=size, digit=digit)
        if self is ValueFormat.String:
            return (
                r"[@\-_!#$%^&+*()\[\]<>?=/\\|`'\"}{~:;,.\w\s]{"
                + re.escape(str(size.min))
                + ","
                + re.escape(str(size.max))
                + "}"
            )
        elif self is ValueFormat.Integer:
            integer_digit = 1 if digit.integer <= 0 else digit.integer
            return r"\d{1," + re.escape(str(integer_digit)) + "}"
        elif self is ValueFormat.BigDecimal:
            integer_digit = 1 if digit.integer <= 0 else digit.integer
            return r"\d{1," + re.escape(str(integer_digit)) + "}\.?\d{0," + re.escape(str(digit.decimal)) + "}"
        elif self is ValueFormat.Boolean:
            return r"(true|false|True|False)"
        elif self is ValueFormat.Enum:
            return r"(" + r"|".join([re.escape(e) for e in enums]) + r")"
        else:
            raise NotImplementedError(f"Doesn't implement what the regex expression should be with format {self}.")

    def _ensure_setting_value_is_valid(self, enums: List[str], size: ValueSize, digit: DigitRange) -> None:
        if self is ValueFormat.String:
            assert size is not None, "The size of string must not be empty."
            assert size.max > 0, f"The maximum size of string must be greater than 0. size: {size}."
            assert size.min >= 0, f"The minimum size of string must be greater or equal to 0. size: {size}."
        elif self is ValueFormat.Integer:
            assert digit is not None, "The digit must not be empty."
            assert digit.integer > 0, f"The digit number must be greater than 0. digit.integer: {digit.integer}."
        elif self is ValueFormat.BigDecimal:
            assert digit is not None, "The digit must not be empty."
            assert (
                digit.integer >= 0
            ), f"The digit number of integer part must be greater or equal to 0. digit.integer: {digit.integer}."
            assert (
                digit.decimal >= 0
            ), f"The digit number of decimal part must be greater or equal to 0. digit.decimal: {digit.decimal}."
        elif self is ValueFormat.Enum:
            assert enums is not None and len(enums) > 0, "The enums must not be empty."
            assert (
                len(list(filter(lambda e: not isinstance(e, str), enums))) == 0
            ), "The data type of element in enums must be string."


class FormatStrategy(Enum):
    BY_DATA_TYPE: str = "by_data_type"
    FROM_ENUMS: str = "from_enums"
    CUSTOMIZE: str = "customize"
    FROM_TEMPLATE: str = "from_template"

    def to_value_format(self, data_type: Union[type, str]) -> ValueFormat:
        if self in [FormatStrategy.CUSTOMIZE, FormatStrategy.FROM_TEMPLATE]:
            raise RuntimeError("It should not convert *FormatStrategy.CUSTOMIZE* to enum object *ValueFormat*.")
        return ValueFormat.to_enum(data_type)

    def generate_not_customize_value(
        self,
        data_type: Optional[type] = None,
        enums: List[str] = [],
        size: ValueSize = Default_Value_Size,
        digit: DigitRange = Default_Digit_Range,
    ) -> Union[str, int, bool, Decimal]:
        if self in [FormatStrategy.BY_DATA_TYPE, FormatStrategy.FROM_ENUMS]:
            assert data_type is not None, "Format setting require *data_type* must not be empty."
            if self is FormatStrategy.FROM_ENUMS:
                data_type = "enum"  # type: ignore[assignment]
            return self.to_value_format(data_type=data_type).generate_value(enums=enums, size=size, digit=digit)
        raise ValueError(f"This function doesn't support *{self}* currently.")
