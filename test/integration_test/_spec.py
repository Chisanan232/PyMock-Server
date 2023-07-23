import inspect
import json
import os
from abc import ABCMeta, abstractmethod
from functools import wraps
from typing import Any, Callable, Optional, Type, Union

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper  # type: ignore

from yaml import dump

from .._values import _Test_Config_Value, _YouTube_API_Content


class file:
    @classmethod
    def write(cls, path: str, content: Union[str, dict], serialize: Optional[Callable] = None) -> None:
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


MockAPI_Config_Yaml_Path: str = "./pytest-api.yaml"
MockAPI_Config_Json_Path: str = "./pytest-api.json"


class _BaseConfigFactory(metaclass=ABCMeta):
    @property
    @abstractmethod
    def file_path(self) -> str:
        pass

    @abstractmethod
    def generate(self) -> None:
        pass

    def delete(self) -> None:
        file.delete(self.file_path)

    def exist(self) -> bool:
        return file.exist(self.file_path)


class yaml_factory(_BaseConfigFactory):
    @property
    def file_path(self) -> str:
        return MockAPI_Config_Yaml_Path

    def generate(self) -> None:
        file.write(self.file_path, content=_Test_Config_Value, serialize=lambda content: dump(content, Dumper=Dumper))


class json_factory(_BaseConfigFactory):
    @property
    def file_path(self) -> str:
        return MockAPI_Config_Json_Path

    def generate(self) -> None:
        file.write(self.file_path, content=_Test_Config_Value, serialize=lambda content: json.dumps(content))


class run_test:
    @classmethod
    def with_file(cls, factory: Type[_BaseConfigFactory]) -> Callable:
        assert factory, "It must set a way to operate configuration file."
        if inspect.isclass(factory) and issubclass(factory, _BaseConfigFactory):
            config_file = factory()
        else:
            assert False, "Decorator's argument cannot accept None value in code usage."

        def _wrap_func(function: Callable) -> Callable:
            @wraps(function)
            def _(self, *args, **kwargs) -> Any:
                # Ensure that it doesn't have file
                config_file.delete()
                # Create the target file before run test
                config_file.generate()
                file.write(
                    path="youtube.json", content=_YouTube_API_Content, serialize=lambda content: json.dumps(content)
                )

                try:
                    # Run the test item
                    function(self, *args, **kwargs)
                finally:
                    # Delete file finally
                    config_file.delete()
                    file.delete("youtube.json")

            return _

        return _wrap_func
