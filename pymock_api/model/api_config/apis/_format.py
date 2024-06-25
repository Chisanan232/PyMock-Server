from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ...enums import FormatStrategy
from .._base import _Checkable, _Config
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
        return self.strategy == other.strategy and self.enums == other.enums and self.variables == other.variables

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
