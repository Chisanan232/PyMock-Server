"""*Read target configuration file and parse its content to data objects*

Read the configuration and parse its content to a specific data object so that it could be convenience to use it.
"""

import os
from abc import ABCMeta, abstractmethod

from yaml import dump, load

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader

# from ..model import APIConfig
# from .converter import Convert


# class Reader(metaclass=ABCMeta):
#     """*The base class which would read configuration and parse its content*"""
#
#     @abstractmethod
#     def load(self, config: str) -> APIConfig:
#         """Load the configuration, parse and deserialize it as data object **APIConfig**.
#
#         Args:
#             config (str): The configuration file path.
#
#         Returns:
#             A **APIConfig** type data object.
#
#         """
#         pass
#
#     @abstractmethod
#     def read(self, config: str) -> dict:
#         """Read the configuration content.
#
#         Args:
#             config (str): The configuration file path.
#
#         Returns:
#             A dict type value which be converted from configuration's content.
#
#         """
#         pass
#
#     @abstractmethod
#     def deserialize(self, data: dict) -> APIConfig:
#         """Deserialize the configuration content into data object **APIConfig**.
#
#         Args:
#             data (dict): The configuration's content which is dict type value.
#
#         Returns:
#             A **APIConfig** type data object.
#
#         """
#         pass
#
#
# class YAMLReader(Reader):
#     """*A reader for YAML format configuration*"""
#
#     def load(self, config: str) -> APIConfig:
#         reading_data = self.read(config)
#         return self.deserialize(reading_data)
#
# def read(self, config: str) -> dict:
#     exist_file = os.path.exists(config)
#     if not exist_file:
#         raise FileNotFoundError(f"The target configuration file {config} doesn't exist.")
#
#     with open(config, "r", encoding="utf-8") as file_stream:
#         data: dict = load(stream=file_stream, Loader=Loader)
#     return data
#
#     def deserialize(self, data: dict) -> APIConfig:
#         return Convert.api_config(data)
#
#
# class YAMLWriter:
#     def serialize(self, config: dict) -> str:
#         return dump(config, Dumper=Dumper)
#
#     def write(self, path: str, config: str) -> None:
#         with open(path, "a+", encoding="utf-8") as file_stream:
#             file_stream.writelines(config)


class YAML:
    def read(self, path: str) -> dict:
        exist_file = os.path.exists(path)
        if not exist_file:
            raise FileNotFoundError(f"The target configuration file {path} doesn't exist.")

        with open(path, "r", encoding="utf-8") as file_stream:
            data: dict = load(stream=file_stream, Loader=Loader)
        return data
