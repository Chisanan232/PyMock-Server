import copy
import logging
import re
from abc import ABC
from dataclasses import dataclass, field
from decimal import Decimal
from pydoc import locate
from typing import Any, Dict, List, Optional, Union

from ._base import _BaseConfig, _Checkable, _Config
from .value import FormatStrategy, ValueFormat
from .variable import Digit, Size, Variable

logger = logging.getLogger(__name__)


@dataclass(eq=False)
class Format(_Config, _Checkable):

    strategy: Optional[FormatStrategy] = None

    # For general --- by data type strategy
    digit: Optional[Digit] = None
    size: Optional[Size] = None

    # For enum strategy
    enums: List[str] = field(default_factory=list)

    # For customize strategy
    customize: str = field(default_factory=str)
    variables: List[Variable] = field(default_factory=list)

    # For from template strategy
    use_name: str = field(default_factory=str)
    # Type is *TemplateConfig*, but it has circular import issue currently.
    _current_template: Any = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.strategy is not None:
            self._convert_strategy()
        if self.digit is not None:
            self._convert_digit()
        if self.size is not None:
            self._convert_size()
        if self.variables is not None:
            self._convert_variables()

    def _convert_strategy(self) -> None:
        if isinstance(self.strategy, str):
            self.strategy = FormatStrategy(self.strategy)

    def _convert_digit(self) -> None:
        if isinstance(self.digit, dict):
            self.digit = Digit().deserialize(self.digit)

    def _convert_size(self) -> None:
        if isinstance(self.size, dict):
            self.size = Size().deserialize(self.size)

    def _convert_variables(self) -> None:
        if not isinstance(self.variables, list):
            raise TypeError(
                f"The data type of key *variables* must be 'list' of 'dict' or '{Variable.__name__}' type data."
            )
        if False in list(map(lambda i: isinstance(i, (dict, Variable)), self.variables)):
            raise TypeError(
                f"The data type of element in key *variables* must be 'dict' or '{Variable.__name__}' type data."
            )
        self.variables = [Variable().deserialize(i) if isinstance(i, dict) else i for i in self.variables]

    def _compare(self, other: "Format") -> bool:
        variables_prop_is_same: bool = True

        # Compare property *variables* size
        if self.variables and other.variables:
            variables_prop_is_same = len(self.variables) == len(other.variables)

        # Compare property *variables* details
        if variables_prop_is_same is True:
            for var in self.variables or []:
                same_name_other_item = list(
                    filter(
                        lambda i: self._find_same_key_var_to_compare(self_var=var, other_var=i), other.variables or []
                    )
                )
                if not same_name_other_item:
                    variables_prop_is_same = False
                    break
                assert len(same_name_other_item) == 1
                if var != same_name_other_item[0]:
                    variables_prop_is_same = False
                    break

        return (
            self.strategy == other.strategy
            and self.digit == other.digit
            and self.size == other.size
            and self.enums == other.enums
            and self.customize == other.customize
            and variables_prop_is_same
        )

    def _find_same_key_var_to_compare(self, self_var: "Variable", other_var: "Variable") -> bool:
        return self_var.name == other_var.name

    @property
    def key(self) -> str:
        return "format"

    @_Config._clean_empty_value
    def serialize(self, data: Optional["Format"] = None) -> Optional[Dict[str, Any]]:
        strategy: FormatStrategy = self.strategy or FormatStrategy(self._get_prop(data, prop="strategy"))

        digit_data_model: Digit = self._get_prop(data, prop="digit")
        digit: dict = digit_data_model.serialize() if digit_data_model else None  # type: ignore[assignment]

        size_data_model: Size = self._get_prop(data, prop="size")
        size_value: Optional[dict] = size_data_model.serialize() if size_data_model else None

        enums: List[str] = self._get_prop(data, prop="enums")
        customize: str = self._get_prop(data, prop="customize")
        variables: List[Variable] = self._get_prop(data, prop="variables")
        use_name: str = self._get_prop(data, prop="use_name")
        serialized_data = {
            "strategy": strategy.value,
            "digit": digit,
            "size": size_value,
            "enums": enums,
            "customize": customize,
            "variables": [var.serialize() if isinstance(var, Variable) else var for var in variables],
            "use_name": use_name,
        }
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["Format"]:

        def _deserialize_variable(d: Dict[str, Any]) -> "Variable":
            variable = Variable()
            variable.absolute_model_key = self.key
            return variable.deserialize(d)

        self.strategy = FormatStrategy(data.get("strategy", None))

        if data.get("digit", None):
            digit_data_model = Digit()
            digit_data_model.absolute_model_key = self.key
            self.digit = digit_data_model.deserialize(data=data.get("digit", None) or {})

        size_value = data.get("size", None)
        if size_value:
            size_data_model = Size()
            size_data_model.absolute_model_key = self.key
            self.size = size_data_model.deserialize(data=size_value or {})
        self.enums = data.get("enums", [])
        self.customize = data.get("customize", "")
        self.variables = [_deserialize_variable(var) for var in (data.get("variables", []) or [])]
        self.use_name = data.get("use_name", "")
        return self

    def is_work(self) -> bool:
        assert self.strategy
        if self.strategy is FormatStrategy.FROM_ENUMS and not self.condition_should_be_true(
            config_key=f"{self.absolute_model_key}.enums",
            condition=(not isinstance(self.enums, list) or (self.enums is not None and len(self.enums) == 0)),
        ):
            return False
        if self.strategy is FormatStrategy.CUSTOMIZE and not self.condition_should_be_true(
            config_key=f"{self.absolute_model_key}.customize",
            condition=(
                not isinstance(self.customize, str) or (self.customize is not None and len(self.customize) == 0)
            ),
        ):
            return False
        if self.strategy is FormatStrategy.FROM_TEMPLATE and not self.condition_should_be_true(
            config_key=f"{self.absolute_model_key}.use_name",
            condition=(not isinstance(self.use_name, str) or (self.use_name is not None and len(self.use_name) == 0)),
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

    def value_format_is_match(self, data_type: Union[str, type], value: Any) -> bool:
        assert self.strategy
        if self.strategy is FormatStrategy.BY_DATA_TYPE:
            data_type = "big_decimal" if isinstance(data_type, float) else data_type
            data_type = locate(data_type) if (data_type != "big_decimal" and isinstance(data_type, str)) else data_type  # type: ignore[assignment]
            digit = self.digit
            if digit is None:
                digit = Digit(integer=128, decimal=128) if data_type == "big_decimal" else Digit()
            size = Size() if self.size is None else self.size
            regex = self.strategy.to_value_format(data_type).generate_regex(
                size=size.to_value_size(), digit=digit.to_digit_range()
            )
            search_result = re.search(regex, str(value))
            if search_result is None:
                # Cannot find any mapping format string
                return False
            return len(str(value)) == len(search_result.group(0))
        elif self.strategy is FormatStrategy.FROM_ENUMS:
            return isinstance(value, str) and value in self.enums
        elif self.strategy is FormatStrategy.CUSTOMIZE:
            all_vars_in_customize = re.findall(r"<\w{1,128}>", str(self.customize), re.IGNORECASE)
            regex = re.escape(copy.copy(self.customize))
            for var in all_vars_in_customize:
                pure_var = var.replace("<", "").replace(">", "")
                find_result = self._get_format_config(pure_var)
                assert find_result[0].value_format
                digit = find_result[0].digit
                if digit is None:
                    digit = (
                        Digit(integer=128, decimal=128)
                        if find_result[0].value_format is ValueFormat.BigDecimal
                        else Digit()
                    )
                size = find_result[0].size  # type: ignore[assignment]
                if size is None:
                    size = Size()
                one_var_regex = find_result[0].value_format.generate_regex(
                    enums=find_result[0].enum or [], size=size.to_value_size(), digit=digit.to_digit_range()
                )
                regex = regex.replace(var, one_var_regex)
            return re.search(regex, str(value), re.IGNORECASE) is not None
        elif self.strategy is FormatStrategy.FROM_TEMPLATE:
            format_config: Format = self._current_template.common_config.format.get_format(self.use_name)
            format_config._current_template = self._current_template
            return format_config.value_format_is_match(data_type=data_type, value=value)
        else:
            raise NotImplementedError(
                f"Doesn't implement how it should generate the response setting by strategy {self}."
            )

    def generate_value(self, data_type: type) -> Union[str, int, bool, Decimal]:
        assert self.strategy
        if self.strategy is FormatStrategy.CUSTOMIZE:
            all_vars_in_customize = re.findall(r"<\w{1,128}>", str(self.customize), re.IGNORECASE)
            value = copy.copy(self.customize)
            for var in all_vars_in_customize:
                pure_var = var.replace("<", "").replace(">", "")
                find_result = self._get_format_config(pure_var)
                assert find_result[0].value_format
                digit = find_result[0].digit
                if digit is None:
                    digit = Digit()
                size = find_result[0].size
                if size is None:
                    size = Size()
                new_value = find_result[0].value_format.generate_value(
                    enums=find_result[0].enum or [], size=size.to_value_size(), digit=digit.to_digit_range()
                )
                value = value.replace(var, str(new_value))
            return value
        elif self.strategy is FormatStrategy.FROM_TEMPLATE:
            format_config: Format = self._current_template.common_config.format.get_format(self.use_name)
            format_config._current_template = self._current_template
            return format_config.generate_value(data_type=data_type)
        else:
            digit = self.digit
            if digit is None:
                digit = Digit()
            size = self.size
            if size is None:
                size = Size()
            return self.strategy.generate_not_customize_value(
                data_type=data_type, enums=self.enums, size=size.to_value_size(), digit=digit.to_digit_range()
            )

    def _get_format_config(self, pure_var: str) -> List[Variable]:
        format_config_in_template: Optional[Variable] = None
        if self._current_template and self._current_template.common_config:
            format_config_in_template = self._current_template.common_config.format.get_variable(pure_var)
        find_result_in_format: List[Variable] = list(filter(lambda v: pure_var == v.name, self.variables))
        find_result = find_result_in_format if find_result_in_format else [format_config_in_template]  # type: ignore[list-item]
        assert len(find_result) == 1 and None not in find_result, "Cannot find the mapping name of variable setting."
        return find_result

    def expect_format_log_msg(self, data_type: type) -> str:
        if self.strategy is FormatStrategy.BY_DATA_TYPE:
            return f"*{data_type}* type data"
        elif self.strategy is FormatStrategy.FROM_ENUMS:
            return f"oen of the enums value *{self.enums}*"
        elif self.strategy is FormatStrategy.CUSTOMIZE:
            return f"like format as *{self.customize}*. Please refer to the property *variables* to know the details of variable settings."
        elif self.strategy is FormatStrategy.FROM_TEMPLATE:
            temp_format: Optional[Format] = self._current_template.common_config.format.get_format(self.use_name)
            assert temp_format is not None
            return temp_format.expect_format_log_msg(data_type=data_type)
        else:
            raise ValueError("Unsupported FormatStrategy")


@dataclass(eq=False)
class _HasFormatPropConfig(_BaseConfig, _Checkable, ABC):
    value_format: Optional[Format] = None

    def __post_init__(self) -> None:
        if self.value_format is not None:
            self._convert_value_format()
        super().__post_init__()

    def _convert_value_format(self) -> None:
        if isinstance(self.value_format, dict):
            self.value_format = Format().deserialize(self.value_format)

    def _compare(self, other: "_HasFormatPropConfig") -> bool:
        return self.value_format == other.value_format and super()._compare(other)

    def serialize(self, data: Optional["_HasFormatPropConfig"] = None) -> Optional[Dict[str, Any]]:
        value_format = (data or self).value_format if (data and data.value_format) or self.value_format else None
        serialized_data = {}
        if value_format:
            serialized_data["format"] = value_format.serialize() if value_format is not None else None

        serialized_data_model = super().serialize(data)  # type: ignore[safe-super]
        if serialized_data_model:
            serialized_data.update(serialized_data_model)
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["_HasFormatPropConfig"]:
        col_format = data.get("format", None)
        if col_format is not None:
            col_format = Format().deserialize(col_format)
        self.value_format = col_format

        super().deserialize(data)  # type: ignore[safe-super]

        # Set section *template* configuration for format feature
        if self.value_format and hasattr(self, "_current_template"):
            self.value_format._current_template = self._current_template
        return self

    def is_work(self) -> bool:
        if self.value_format:
            self.value_format.stop_if_fail = self.stop_if_fail
            if not self.value_format.is_work():
                return False

        is_work = super().is_work()  # type: ignore[safe-super]
        if is_work is False:
            return False
        return True

    def generate_value_by_format(
        self, data_type: Optional[type] = None, default: str = "no default"
    ) -> Union[str, int, bool, Decimal]:
        if self.value_format is not None:
            assert data_type is not None, "Format setting require *data_type* must not be empty."
            value = self.value_format.generate_value(data_type=data_type)
        else:
            value = default
        return value
