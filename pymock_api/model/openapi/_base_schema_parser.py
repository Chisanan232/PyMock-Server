import copy
import json
import pathlib
from abc import ABCMeta, abstractmethod
from typing import Dict, List


class BaseSchemaParser(metaclass=ABCMeta):
    def __init__(self, data: dict):
        self._data = copy.copy(data)

    @property
    def current_data(self) -> dict:
        return self._data


class BaseOpenAPITagSchemaParser(BaseSchemaParser):

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_description(self):
        pass


class BaseOpenAPISchemaParser(BaseSchemaParser):

    def __init__(self, file: str = "", data: Dict = {}):
        super().__init__(data=data)

        if file:
            file_path = pathlib.Path(file)
            if not file_path.exists():
                raise FileNotFoundError(f"Cannot find the OpenAPI format configuration at file path *{file_path}*.")
            with open(str(file_path), "r", encoding="utf-8") as io_stream:
                self._data = json.load(io_stream)

        assert self._data, "No any data. Parse OpenAPI config fail."

    @abstractmethod
    def get_paths(self) -> Dict[str, Dict]:
        pass

    @abstractmethod
    def get_tags(self) -> List[dict]:
        pass

    @abstractmethod
    def get_objects(self) -> Dict[str, dict]:
        pass
