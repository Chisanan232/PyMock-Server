import re
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Union

from fake_api_server._utils.random import (
    DigitRange,
    RandomBigDecimal,
    RandomBoolean,
    RandomDate,
    RandomDateTime,
    RandomEMail,
    RandomFromSequence,
    RandomInteger,
    RandomIP,
    RandomString,
    RandomURI,
    RandomUUID,
    ValueSize,
)
from fake_api_server._utils.uri_protocol import IPVersion, URIScheme

Default_Value_Size = ValueSize(max=10, min=1)
Default_Digit_Range = DigitRange(integer=128, decimal=128)


class ValueFormat(Enum):
    # general format
    String = "str"
    Integer = "int"
    BigDecimal = "big_decimal"
    Boolean = "bool"
    Date = "date"
    DateTime = "date-time"
    Enum = "enum"

    # specific format
    EMail = "email"
    UUID = "uuid"
    URI = "uri"
    URL = "url"
    # Hostname = "hostname"
    IPv4 = "ipv4"
    IPv6 = "ipv6"

    @property
    def _nothin_need_to_check(self) -> List["ValueFormat"]:
        return [
            ValueFormat.Date,
            ValueFormat.DateTime,
            ValueFormat.EMail,
            ValueFormat.UUID,
            ValueFormat.URI,
            ValueFormat.URL,
            ValueFormat.IPv4,
            ValueFormat.IPv6,
        ]

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
        elif self is ValueFormat.Date:
            return RandomDate.generate()
        elif self is ValueFormat.DateTime:
            return RandomDateTime.generate()
        elif self is ValueFormat.Enum:
            return RandomFromSequence.generate(enums)
        elif self is ValueFormat.EMail:
            return RandomEMail.generate()
        elif self is ValueFormat.UUID:
            return RandomUUID.generate()
        elif self is ValueFormat.URI:
            # TODO: It should has setting to configure URI scheme
            return RandomURI.generate(scheme=URIScheme.HTTPS)
        elif self is ValueFormat.URL:
            return RandomURI.generate(scheme=URIScheme.HTTPS)
        elif self is ValueFormat.IPv4:
            return RandomIP.generate(IPVersion.IPv4)
        elif self is ValueFormat.IPv6:
            return RandomIP.generate(IPVersion.IPv4)
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
        elif self is ValueFormat.Date:
            return r"\d{4}-\d{1,2}-\d{1,2}"
        elif self is ValueFormat.DateTime:
            return r"\d{4}-\d{1,2}-\d{1,2}T\d{1,2}:\d{1,2}:\d{1,2}Z"
        elif self is ValueFormat.Enum:
            return r"(" + r"|".join([re.escape(e) for e in enums]) + r")"
        elif self is ValueFormat.EMail:
            return r"\w{1,124}@(gmail|outlook|yahoo).com"
        elif self is ValueFormat.UUID:
            return r"\w{8}-\w{4}-\w{4}-\w{4}-\w{12}"
        elif self is ValueFormat.URI:
            # TODO: It should has setting to configure URI scheme
            return URIScheme.HTTPS.generate_value_regex()
        elif self is ValueFormat.URL:
            return URIScheme.HTTPS.generate_value_regex()
        elif self is ValueFormat.IPv4:
            return r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        elif self is ValueFormat.IPv6:
            return r"(\d|[a-f]){4}:(\d|[a-f]){4}:(\d|[a-f]){4}:(\d|[a-f]){4}:(\d|[a-f]){4}:(\d|[a-f]){4}:(\d|[a-f]){4}:(\d|[a-f]){4}"
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
        elif self in self._nothin_need_to_check:
            # TODO: Add some settings for datetime value
            assert True
        elif self is ValueFormat.Enum:
            assert enums is not None and len(enums) > 0, "The enums must not be empty."
            assert (
                len(list(filter(lambda e: not isinstance(e, str), enums))) == 0
            ), "The data type of element in enums must be string."


class FormatStrategy(Enum):
    BY_DATA_TYPE = "by_data_type"
    FROM_ENUMS = "from_enums"
    CUSTOMIZE = "customize"
    FROM_TEMPLATE = "from_template"

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
