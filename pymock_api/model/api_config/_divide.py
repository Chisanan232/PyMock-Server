import os
import pathlib
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Union

from ..._utils import YAML
from ..._utils.file_opt import _BaseFileOperation
from ._base import _Config
from .template import _TemplatableConfig


@dataclass(eq=False)
class _DivideStrategy:
    divide_api: bool = field(default=False)
    divide_http: bool = field(default=False)
    divide_http_request: bool = field(default=False)
    divide_http_response: bool = field(default=False)


class _BeDividedable(metaclass=ABCMeta):
    tag: str = field(init=False, repr=False)
    api_name: str = field(init=False, repr=False)


class _Dividable(metaclass=ABCMeta):
    dry_run: bool = field(init=False, repr=False, default=True)

    _divide_strategy: _DivideStrategy = _DivideStrategy()

    _configuration: _BaseFileOperation = YAML()

    @property
    @abstractmethod
    def should_divide(self) -> bool:
        pass

    @property
    def save_data(self) -> bool:
        return self.dry_run is False

    @property
    def should_set_bedividedable_value(self) -> bool:
        return not self.should_divide or (self.should_divide and not self.save_data)

    def _process_dividing_serialize(
        self,
        data_modal: Union[_Config, _BeDividedable],
        init_data: Dict[str, Any],
        api_name: str,
        tag: str = "",
        key: str = "",
        should_set_dividable_value_callback: Optional[Callable] = None,
    ) -> None:
        assert isinstance(data_modal, _Config) and isinstance(data_modal, _BeDividedable)
        # Pre-process
        if isinstance(data_modal, _Dividable):
            data_modal.dry_run = self.dry_run
        data_modal.api_name = api_name
        if tag:
            data_modal.tag = tag
        # Run dividing serialization
        serialized_data = self.dividing_serialize(data=data_modal)
        # Set the dividing serialization if it needs
        if not should_set_dividable_value_callback:
            should_set_dividable_value_callback = lambda: self.should_set_bedividedable_value
        if should_set_dividable_value_callback():
            self._set_serialized_data(init_data, serialized_data, key)

    @abstractmethod
    def _set_serialized_data(
        self, init_data: Dict[str, Any], serialized_data: Optional[Union[str, dict]], key: str = ""
    ) -> None:
        pass

    def dividing_serialize(
        self, data: Union[_Config, _BeDividedable, _TemplatableConfig]
    ) -> Optional[Union[str, dict]]:
        if self.should_divide:
            assert (
                isinstance(data, _Config) and isinstance(data, _BeDividedable) and isinstance(data, _TemplatableConfig)
            )
            config_base_path = data._current_template.values.base_file_path
            tag_dir = str(pathlib.Path(config_base_path, data.tag)) if data.tag else ""
            config_file = f"{data.api_name}-{data.key.replace('<mock API>', 'api')}.yaml"
            path = pathlib.Path(config_base_path, data.tag, config_file)
            if self.save_data:
                if tag_dir and not os.path.exists(tag_dir):
                    os.mkdir(tag_dir)
                self._configuration.write(path=str(path), config=self.serialize_lower_layer(data=data))
                return
            else:
                return str(path)
        else:
            return self.serialize_lower_layer(data=data)

    def serialize_lower_layer(
        self, data: Union[_Config, _BeDividedable, _TemplatableConfig]
    ) -> Optional[Dict[str, Any]]:
        return data.serialize()  # type: ignore[union-attr]
