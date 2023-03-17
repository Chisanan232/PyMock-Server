import os
from typing import Any, Callable, Union

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper
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


MockAPI_Config_Path: str = "./pytest-api.yaml"


class ConfigFile:
    @property
    def file_path(self) -> str:
        return MockAPI_Config_Path

    def generate(self) -> None:
        file.write(self.file_path, content=_Test_Config_Value, serialize=lambda content: dump(content, Dumper=Dumper))

    def delete(self) -> None:
        file.delete(self.file_path)

    def exist(self) -> bool:
        return file.exist(self.file_path)


class run_test:
    config_file: ConfigFile = ConfigFile()

    @classmethod
    def with_file(cls, fixture: Any = None) -> Callable:
        def _test_wrapper(function: Callable) -> Callable:
            def _(self) -> Any:
                # Ensure that it doesn't have file
                cls.config_file.delete()
                # Create the target file before run test
                cls.config_file.generate()

                try:
                    # Run the test item
                    return_value = function(self, fixture)
                finally:
                    # Delete file finally
                    cls.config_file.delete()
                return return_value

            return _

        return _test_wrapper
