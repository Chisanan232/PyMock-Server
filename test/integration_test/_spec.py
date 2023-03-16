import os
from abc import ABCMeta, abstractmethod
from typing import Callable, Optional, Union

from yaml import CDumper as Dumper
from yaml import dump

from .._values import _Test_Config_Value


class file:
    @classmethod
    def write(cls, path: str, content: Union[str, dict], serialize: Callable = None) -> None:
        if not serialize:
            serialize = lambda dataraw: dataraw
        with open(path, "a+", encoding="utf-8") as file_stream:
            output = serialize(content)
            file_stream.writelines(output)

    @classmethod
    def delete(cls, path: str) -> None:
        if cls.exist(path):
            os.remove(path)
        exist_file = cls.exist(path)
        assert exist_file is False, "File should already be removed."

    @classmethod
    def exist(cls, path: str) -> bool:
        return os.path.exists(path)


class ConfigFile(metaclass=ABCMeta):
    @property
    @abstractmethod
    def file_path(self) -> str:
        pass

    def generate(self) -> None:
        file.write(self.file_path, content=_Test_Config_Value, serialize=lambda content: dump(content, Dumper=Dumper))

    def _delete_file(self, path: Optional[str] = None) -> None:
        if not path:
            path = self.file_path
        if self._exist_file(path):
            os.remove(path)
        exist_file = self._exist_file(path)
        assert exist_file is False, "File should already be removed."

    def _exist_file(self, path: Optional[str] = None) -> bool:
        if not path:
            path = self.file_path
        return os.path.exists(path)

    @staticmethod
    def _test_with_file(function):
        def _(self):
            # Ensure that it doesn't have file
            self._delete_file()
            # Create the target file before run test
            self.generate()

            try:
                # Run the test item
                function(self)
            finally:
                # Delete file finally
                self._delete_file()

        return _
