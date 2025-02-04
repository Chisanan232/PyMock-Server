from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from fake_api_server._utils.random import DigitRange, RandomInteger, ValueSize

from ._base import _Checkable, _Config
from .value import ValueFormat


@dataclass(eq=False)
class Digit(_Config, _Checkable):
    _default_integer: int = 8
    _default_decimal: int = 4

    integer: int = _default_integer
    decimal: int = _default_decimal

    def _compare(self, other: "Digit") -> bool:
        return self.integer == other.integer and self.decimal == other.decimal

    @property
    def key(self) -> str:
        return "digit"

    def serialize(self, data: Optional["Digit"] = None) -> Optional[Dict[str, Any]]:
        integer: int = self._get_prop(data, prop="integer")
        decimal: int = self._get_prop(data, prop="decimal")
        serialized_data = {
            "integer": (integer if integer is not None else self._default_integer),
            "decimal": (decimal if decimal is not None else self._default_decimal),
        }
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["Digit"]:
        self.integer = data.get("integer", self._default_integer)
        self.decimal = data.get("decimal", self._default_decimal)
        return self

    def is_work(self) -> bool:
        under_check_props = {
            f"{self.absolute_model_key}.integer": self.integer,
            f"{self.absolute_model_key}.decimal": self.decimal,
        }
        if not self.props_should_not_be_none(
            under_check=under_check_props,
            accept_empty=False,
        ):
            return False
        for prop_key, prop_val in under_check_props.items():
            if not self.condition_should_be_true(
                config_key=prop_key,
                condition=(prop_val is not None and not isinstance(prop_val, int)),
            ):
                return False
        return True

    def to_digit_range(self) -> DigitRange:
        return DigitRange(integer=self.integer, decimal=self.decimal)


@dataclass(eq=False)
class Size(_Config, _Checkable):
    _default_max_value: int = 10
    _default_min_value: int = 0

    max_value: int = _default_max_value
    min_value: int = _default_min_value
    only_equal: Optional[int] = None

    def _compare(self, other: "Size") -> bool:
        return (
            self.max_value == other.max_value
            and self.min_value == other.min_value
            and self.only_equal == other.only_equal
        )

    @property
    def key(self) -> str:
        return "size"

    @_Config._clean_empty_value
    def serialize(self, data: Optional["Size"] = None) -> Optional[Dict[str, Any]]:
        max_value: int = self._get_prop(data, prop="max_value")
        min_value: int = self._get_prop(data, prop="min_value")
        only_equal: int = self._get_prop(data, prop="only_equal")
        serialized_data = {
            "max": (max_value if max_value is not None else self._default_max_value),
            "min": (min_value if min_value is not None else self._default_min_value),
            "only_equal": only_equal,
        }
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["Size"]:
        self.min_value = data.get("min", self._default_min_value)
        self.max_value = data.get("max", self._default_max_value)
        self.only_equal = data.get("only_equal", None)
        return self

    def is_work(self) -> bool:
        under_check_props = {
            f"{self.absolute_model_key}.max": self.max_value,
            f"{self.absolute_model_key}.min": self.min_value,
        }
        if not self.props_should_not_be_none(
            under_check=under_check_props,
            accept_empty=False,
        ):
            return False
        for prop_key, prop_val in under_check_props.items():
            if not self.condition_should_be_true(
                config_key=prop_key,
                condition=(prop_val is not None and not isinstance(prop_val, int)),
            ):
                return False

        if self.only_equal and not self.condition_should_be_true(
            config_key=f"{self.absolute_model_key}.only_equal",
            condition=(self.only_equal is not None and not isinstance(self.only_equal, int)),
        ):
            return False
        return True

    def to_value_size(self) -> ValueSize:
        if self.only_equal:
            return ValueSize(max=self.only_equal, min=self.only_equal)
        else:
            return ValueSize(max=self.max_value, min=self.min_value)

    def generate_random_int(self) -> int:
        return RandomInteger.generate(value_range=self.to_value_size())


@dataclass(eq=False)
class Variable(_Config, _Checkable):
    name: str = field(default_factory=str)
    value_format: Optional[ValueFormat] = None
    digit: Optional[Digit] = None
    size: Optional[Size] = None
    enum: Optional[List[str]] = None

    _absolute_key: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.value_format is not None:
            self._convert_value_format()
        if self.digit is not None:
            self._convert_digit()
        if self.size is not None:
            self._convert_size()

    def _convert_value_format(self) -> None:
        if isinstance(self.value_format, str):
            self.value_format = ValueFormat.to_enum(self.value_format)

    def _convert_digit(self) -> None:
        if isinstance(self.digit, dict):
            self.digit = Digit().deserialize(self.digit)

    def _convert_size(self) -> None:
        if isinstance(self.size, dict):
            self.size = Size().deserialize(self.size)

    def _compare(self, other: "Variable") -> bool:
        return (
            self.name == other.name
            and self.value_format == other.value_format
            and self.digit == other.digit
            and self.size == other.size
            and self.enum == other.enum
        )

    @property
    def key(self) -> str:
        return "<variable>"

    @_Config._clean_empty_value
    def serialize(self, data: Optional["Variable"] = None) -> Optional[Dict[str, Any]]:
        name: str = self._get_prop(data, prop="name")

        value_format: ValueFormat = self.value_format or ValueFormat.to_enum(self._get_prop(data, prop="value_format"))

        digit_data_model: Digit = (self or data).digit  # type: ignore[union-attr,assignment]
        digit: dict = digit_data_model.serialize() if digit_data_model else None  # type: ignore[assignment]

        size_data_model: Size = (self or data).size  # type: ignore[union-attr,assignment]
        size_value: Optional[dict] = size_data_model.serialize() if size_data_model else None

        enum: str = self._get_prop(data, prop="enum")
        if not name or not value_format:
            return None
        serialized_data = {
            "name": name,
            "value_format": value_format.value,
            "digit": digit,
            "size": size_value,
            "enum": enum,
        }
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["Variable"]:
        self.name = data.get("name", None)

        self.value_format = ValueFormat.to_enum(data.get("value_format", None))
        if not self.value_format:
            raise ValueError("Schema key *value_format* cannot be empty.")

        if self.value_format == ValueFormat.Enum:
            self.enum = data.get("enum", None)
        else:
            digit_value = data.get("digit", None)
            if digit_value:
                digit_data_model = Digit()
                digit_data_model.absolute_model_key = self.key
                self.digit = digit_data_model.deserialize(data=digit_value or {})

        size_value = data.get("size", None)
        if size_value:
            size_data_model = Size()
            size_data_model.absolute_model_key = self.key
            self.size = size_data_model.deserialize(data=size_value or {})
        return self

    def is_work(self) -> bool:
        if not self.props_should_not_be_none(
            under_check={
                f"{self.absolute_model_key}.name": self.name,
            },
            accept_empty=False,
        ):
            return False
        assert self.value_format
        if self.value_format is ValueFormat.Enum and not self.props_should_not_be_none(
            under_check={
                f"{self.absolute_model_key}.enum": self.enum,
            },
            accept_empty=False,
        ):
            return False

        if self.digit is not None:
            self.digit.stop_if_fail = self.stop_if_fail
            if self.digit.is_work() is False:
                return False

        if self.size is not None:
            self.size.stop_if_fail = self.stop_if_fail
            if self.size.is_work() is False:
                return False

        return True
