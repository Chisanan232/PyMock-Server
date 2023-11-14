import os
import pathlib
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

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
    tag: str = field(init=False, repr=False, compare=False)
    api_name: str = field(init=False, repr=False, compare=False)


class _Dividable(metaclass=ABCMeta):
    _divide_strategy: _DivideStrategy = _DivideStrategy()

    _configuration: _BaseFileOperation = YAML()

    @property
    @abstractmethod
    def should_divide(self) -> bool:
        pass

    def dividing_serialize(
        self, data: Union[_Config, _BeDividedable, _TemplatableConfig], save_data: bool
    ) -> Optional[Union[str, dict]]:
        if self.should_divide:
            assert (
                isinstance(data, _Config) and isinstance(data, _BeDividedable) and isinstance(data, _TemplatableConfig)
            )
            config_base_path = data._current_template.values.base_file_path
            tag_dir = str(pathlib.Path(config_base_path, data.tag)) if data.tag else ""
            config_file = f"{data.api_name}_{data.key}.yaml"
            path = pathlib.Path(tag_dir, config_base_path, config_file)
            if save_data:
                if tag_dir and not os.path.exists(tag_dir):
                    os.mkdir(tag_dir)
                self._configuration.write(path=str(path), config=self.serialize_lower_layer(data=data))
                return
            else:
                return str(path)
        else:
            return self.serialize_lower_layer(data=data)

    @abstractmethod
    def serialize_lower_layer(
        self, data: Union[_Config, _BeDividedable, _TemplatableConfig]
    ) -> Optional[Dict[str, Any]]:
        pass
