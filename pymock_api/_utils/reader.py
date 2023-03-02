"""*Read target configuration file and parse its content to data objects*

Read the configuration and parse its content to a specific data object so that it could be convenience to use it.
"""

from abc import ABCMeta, abstractmethod

from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from pymock_api._utils.converter import Convert
from pymock_api.model.api_config import APIConfig


class Reader(metaclass=ABCMeta):
    """*The base class which would read configuration and parse its content*"""

    @abstractmethod
    def load(self, config: str) -> APIConfig:
        """Load the configuration, parse and deserialize it as data object **APIConfig**.

        Args:
            config (str): The configuration file path.

        Returns:
            A **APIConfig** type data object.

        """
        pass

    @abstractmethod
    def read(self, config: str) -> dict:
        """Read the configuration content.

        Args:
            config (str): The configuration file path.

        Returns:
            A dict type value which be converted from configuration's content.

        """
        pass

    @abstractmethod
    def deserialize(self, data: dict) -> APIConfig:
        """Deserialize the configuration content into data object **APIConfig**.

        Args:
            data (dict): The configuration's content which is dict type value.

        Returns:
            A **APIConfig** type data object.

        """
        pass


class YAMLReader(Reader):
    """*A reader for YAML format configuration*"""

    def load(self, config: str) -> APIConfig:
        reading_data = self.read(config)
        return self.deserialize(reading_data)

    def read(self, config: str) -> dict:
        with open(config, "r", encoding="utf-8") as file_stream:
            data: dict = load(stream=file_stream, Loader=Loader)
        return data

    def deserialize(self, data: dict) -> APIConfig:
        return Convert.api_config(data)
