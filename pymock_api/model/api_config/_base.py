import sys
from abc import ABCMeta, abstractmethod
from dataclasses import field
from typing import Any, Callable, Dict, Optional

# The truly semantically is more near like following:
#
# ConfigType = TypeVar("ConfigType" bound="_Config")
# def need_implement_func(param: ConfigType):
#     ... (implementation)
#
# However, it would have mypy issue:
# error: Argument 1 of "{method}" is incompatible with supertype "_Config"; supertype defines the argument type as
# "ConfigType"  [override]
# note: This violates the Liskov substitution principle
# note: See https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides
SelfType = Any


class _Config(metaclass=ABCMeta):
    _absolute_key: str = field(init=False, repr=False)

    def __eq__(self, other: SelfType) -> bool:
        if other is None:
            return False
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"Cannot run equal operation between these 2 objects because of their data types is different. Be "
                f"operated object: {type(self)}, another object: {type(other)}."
            )
        return self._compare(other)

    @abstractmethod
    def _compare(self, other: SelfType) -> bool:
        pass

    @property
    def absolute_model_key(self) -> str:
        return self._absolute_key

    @absolute_model_key.setter
    def absolute_model_key(self, key: str) -> None:
        self._absolute_key = key
        if self._absolute_key:
            self._absolute_key += f".{self.key}"

    @property
    @abstractmethod
    def key(self) -> str:
        pass

    @abstractmethod
    def serialize(self, data: Optional[SelfType] = None) -> Optional[Dict[str, Any]]:
        pass

    @staticmethod
    def _ensure_process_with_not_empty_value(function: Callable) -> Callable:
        def _(self, data: Dict[str, Any]) -> Optional[SelfType]:
            if not data:
                return data
            return function(self, data)

        return _

    @abstractmethod
    def deserialize(self, data: Dict[str, Any]) -> Optional[SelfType]:
        pass

    def _get_prop(self, data: Optional[object], prop: str) -> Any:
        if not hasattr(data, prop) and not hasattr(self, prop):
            raise AttributeError(f"Cannot find attribute {prop} in objects {data} or {self}.")
        return (getattr(data, prop) if data else None) or getattr(self, prop)

    @abstractmethod
    def is_work(self) -> bool:
        pass


class _Checkable(metaclass=ABCMeta):
    _stop_if_fail: Optional[bool] = field(init=False, repr=False, default=None)
    _config_is_wrong: bool = field(init=False, repr=False, default=False)

    def should_not_be_none(
        self,
        config_key: str,
        config_value: Any,
        valid_callback: Optional[Callable] = None,
        err_msg: Optional[str] = None,
    ) -> bool:
        if config_value is None:
            print(err_msg if err_msg else f"Configuration *{config_key}* content cannot be empty.")
            self._config_is_wrong = True
            if self._stop_if_fail:
                self._exit_program(1)
            return False
        else:
            if valid_callback:
                return valid_callback(config_key, config_value)
            return True

    def should_be_valid(
        self, config_key: str, config_value: Any, criteria: list, valid_callback: Optional[Callable] = None
    ) -> None:
        if not isinstance(criteria, list):
            raise TypeError("The argument *criteria* only accept 'list' type value.")

        if config_value not in criteria:
            is_valid = False
        else:
            is_valid = True

        if not is_valid:
            print(f"Configuration *{config_key}* value is invalid.")
            self._config_is_wrong = True
            if self._stop_if_fail:
                self._exit_program(1)
        else:
            if valid_callback:
                valid_callback(config_key, config_value, criteria)

    def run_finally(self) -> None:
        if self._config_is_wrong:
            print("Configuration is invalid.")
            if self._stop_if_fail:
                self._exit_program(1)
        else:
            print("Configuration is valid.")
            self._exit_program(0)

    def _exit_program(self, exit_code: int = 0, msg: str = "") -> None:
        if msg:
            print(msg)
        sys.exit(exit_code)
