"""*Read target configuration file and parse its content to data objects*

Read the configuration and parse its content to a specific data object so that it could be convenience to use it.
"""

import json
import os
from abc import ABCMeta, abstractmethod
from typing import Union

from yaml import dump, load

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader  # type: ignore


class _BaseFileOperation(metaclass=ABCMeta):
    @abstractmethod
    def read(self, path: str) -> dict:
        pass

    @abstractmethod
    def write(self, path: str, config: Union[str, dict], mode: str = "a+") -> None:
        pass

    @abstractmethod
    def serialize(self, config: dict) -> str:
        pass


class YAML(_BaseFileOperation):
    def read(self, path: str) -> dict:
        exist_file = os.path.exists(path)
        if not exist_file:
            raise FileNotFoundError(f"The target configuration file {path} doesn't exist.")

        with open(path, "r", encoding="utf-8") as file_stream:
            data: dict = load(stream=file_stream, Loader=Loader)
        return data

    def write(self, path: str, config: Union[str, dict], mode: str = "a+") -> None:
        yaml_content = self.serialize(config) if isinstance(config, dict) else config
        with open(path, mode, encoding="utf-8") as file_stream:
            file_stream.writelines(yaml_content)

    def serialize(self, config: dict) -> str:
        return dump(config, Dumper=Dumper, sort_keys=False)


class JSON(_BaseFileOperation):
    def read(self, path: str) -> dict:
        exist_file = os.path.exists(path)
        if not exist_file:
            raise FileNotFoundError(f"The target configuration file {path} doesn't exist.")

        with open(path, "r", encoding="utf-8") as file_stream:
            data: dict = json.loads(file_stream.read())
        return data

    def write(self, path: str, config: Union[str, dict], mode: str = "a+") -> None:
        json_content = self.serialize(config) if isinstance(config, dict) else config
        with open(path, mode, encoding="utf-8") as file_stream:
            file_stream.writelines(json_content)

    def serialize(self, config: dict) -> str:
        return json.dumps(config, indent=4)
