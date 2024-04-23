import sys
from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type

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

    @property
    def stop_if_fail(self) -> Optional[bool]:
        return self._stop_if_fail

    @stop_if_fail.setter
    def stop_if_fail(self, s: bool) -> None:
        self._stop_if_fail = s

    def should_not_be_none(
        self,
        config_key: str,
        config_value: Any,
        accept_empty: bool = True,
        valid_callback: Optional[Callable] = None,
        err_msg: Optional[str] = None,
    ) -> bool:
        if (config_value is None) or (accept_empty and not config_value):
            print(err_msg if err_msg else f"Configuration *{config_key}* content cannot be empty.")
            self._config_is_wrong = True
            if self._stop_if_fail:
                self._exit_program(1)
            return False
        else:
            if valid_callback:
                return valid_callback(config_key, config_value)
            return True

    def props_should_not_be_none(
        self,
        under_check: dict,
        accept_empty: bool = True,
        valid_callback: Optional[Callable] = None,
        err_msg: Optional[str] = None,
    ) -> bool:
        for k, v in under_check.items():
            if not self.should_not_be_none(
                config_key=k,
                config_value=v,
                accept_empty=accept_empty,
                valid_callback=valid_callback,
                err_msg=err_msg,
            ):
                return False
        return True

    def should_be_valid(
        self, config_key: str, config_value: Any, criteria: list, valid_callback: Optional[Callable] = None
    ) -> bool:
        assert isinstance(criteria, list), "The argument *criteria* only accept 'list' type value."

        is_valid = config_value in criteria
        if not is_valid:
            print(f"Configuration *{config_key}* value is invalid.")
            self._config_is_wrong = True
            if self._stop_if_fail:
                self._exit_program(1)
        else:
            if valid_callback:
                valid_callback(config_key, config_value, criteria)
        return is_valid

    def condition_should_be_true(
        self,
        config_key: str,
        condition: bool,
        err_msg: Optional[str] = None,
    ) -> bool:
        if condition is True:
            base_error_msg = f"Configuration *{config_key}* setting is invalid."
            print(f"{base_error_msg} {err_msg}" if err_msg else base_error_msg)
            self._config_is_wrong = True
            if self._stop_if_fail:
                self._exit_program(1)
            return False
        else:
            return True

    def _exit_program(self, exit_code: int = 0, msg: str = "") -> None:
        if msg:
            print(msg)
        sys.exit(exit_code)


@dataclass(eq=False)
class _HasItemsPropConfig(_Config, _Checkable, ABC):
    items: Optional[List["_HasItemsPropConfig"]] = None

    def _compare(self, other: "_HasItemsPropConfig") -> bool:
        return self.items == other.items

    def __post_init__(self) -> None:
        if self.items is not None:
            self._convert_items()

    def _convert_items(self):
        if False in list(map(lambda i: isinstance(i, (dict, self._item_type())), self.items)):
            raise TypeError(
                f"The data type of key *items* must be 'dict' or '{_HasItemsPropConfig.__name__}' type data."
            )
        self.items = [self._deserialize_item_with_data(i) if isinstance(i, dict) else i for i in self.items]

    @abstractmethod
    def _item_type(self) -> Type["_HasItemsPropConfig"]:
        pass

    @abstractmethod
    def _deserialize_empty_item(self) -> "_HasItemsPropConfig":
        pass

    @abstractmethod
    def _deserialize_item_with_data(self, i: dict) -> "_HasItemsPropConfig":
        pass

    def serialize(self, data: Optional["_HasItemsPropConfig"] = None) -> Optional[Dict[str, Any]]:
        serialized_data = {}
        items = self._get_prop(data, prop="items")
        if items:
            serialized_data["items"] = [
                item.serialize() if isinstance(item, self._item_type()) else item for item in items
            ]
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["_HasItemsPropConfig"]:
        items = [
            self._deserialize_empty_item().deserialize(item) if isinstance(item, dict) else item
            for item in (data.get("items", []) or [])
        ]
        self.items = items if items else None
        return self

    def is_work(self) -> bool:
        if self.items:

            def _i_is_work(i: "_HasItemsPropConfig") -> bool:
                i.stop_if_fail = self.stop_if_fail
                return i.is_work()

            is_work_props = list(filter(lambda i: _i_is_work(i), self.items))
            if len(is_work_props) != len(self.items):
                return False
        return True
