import copy
import re
from abc import ABC
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

from ...enums import FormatStrategy
from .._base import _BaseConfig, _Checkable, _Config
from ..variable import Variable


@dataclass(eq=False)
class Format(_Config, _Checkable):

    strategy: Optional[FormatStrategy] = None
    enums: List[str] = field(default_factory=list)
    customize: str = field(default_factory=str)
    variables: List[Variable] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.strategy is not None:
            self._convert_strategy()
        if self.variables is not None:
            self._convert_variables()

    def _convert_strategy(self) -> None:
        if isinstance(self.strategy, str):
            self.strategy = FormatStrategy.to_enum(self.strategy)

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
        strategy: FormatStrategy = self.strategy or FormatStrategy.to_enum(self._get_prop(data, prop="strategy"))
        enums: List[str] = self._get_prop(data, prop="enums")
        customize: str = self._get_prop(data, prop="customize")
        variables: List[Variable] = self._get_prop(data, prop="variables")
        if not strategy:
            return None
        serialized_data = {
            "strategy": strategy.value,
            "enums": enums,
            "customize": customize,
            "variables": [var.serialize() if isinstance(var, Variable) else var for var in variables],
        }
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["Format"]:

        def _deserialize_variable(d: Dict[str, Any]) -> "Variable":
            variable = Variable()
            variable.absolute_model_key = self.key
            return variable.deserialize(d)

        self.strategy = FormatStrategy.to_enum(data.get("strategy", None))
        if not self.strategy:
            raise ValueError("Schema key *strategy* cannot be empty.")
        self.enums = data.get("enums", [])
        self.customize = data.get("customize", "")
        self.variables = [_deserialize_variable(var) for var in (data.get("variables", []) or [])]
        return self

    def is_work(self) -> bool:
        assert self.strategy
        if self.strategy is FormatStrategy.FROM_ENUMS and not self.props_should_not_be_none(
            under_check={
                f"{self.absolute_model_key}.enums": self.enums,
            },
            accept_empty=False,
        ):
            return False
        if self.strategy is FormatStrategy.CUSTOMIZE and not self.props_should_not_be_none(
            under_check={
                f"{self.absolute_model_key}.customize": self.customize,
            },
            accept_empty=False,
        ):
            return False
        return True

    def value_format_is_match(self, value: Any, enums: List[str] = [], customize: str = "") -> bool:
        assert self.strategy
        return self.strategy.chk_format_is_match(value=value, enums=enums, customize=customize)

    def generate_value(self) -> Union[str, int, bool, Decimal]:
        assert self.strategy
        if self.strategy is FormatStrategy.CUSTOMIZE:
            all_vars_in_customize = re.findall(r"<\w{1,128}>", str(self.customize), re.IGNORECASE)
            value = copy.copy(self.customize)
            for var in all_vars_in_customize:
                pure_var = var.replace("<", "").replace(">", "")
                find_result: List[Variable] = list(filter(lambda v: pure_var == v.name, self.variables))
                assert len(find_result) == 1, "Cannot find the mapping name of variable setting."
                assert find_result[0].value_format
                new_value = find_result[0].value_format.generate_value(enums=find_result[0].enum or [])
                value = value.replace(var, str(new_value))
            return value
        else:
            return self.strategy.generate_not_customize_value(enums=self.enums)


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

    def generate_value_by_format(self, default: str = "no default") -> Union[str, int, bool, Decimal]:
        if self.value_format is not None:
            value = self.value_format.generate_value()
        else:
            value = default
        return value
