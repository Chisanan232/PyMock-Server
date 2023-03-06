import json
import os
from abc import ABCMeta, abstractmethod
from typing import Optional, Union

from yaml import CDumper as Dumper
from yaml import dump

from .._values import _Test_Config_Value


class SpecWithFileOpt(metaclass=ABCMeta):
    @property
    @abstractmethod
    def file_path(self) -> str:
        pass

    def _write_test_file(self) -> None:
        with open(self.file_path, "a+", encoding="utf-8") as file_stream:
            output = dump(_Test_Config_Value, Dumper=Dumper)
            file_stream.writelines(output)

    def _write_json_file(self, path: str, content: Union[str, dict]) -> None:
        with open(path, "a+", encoding="utf-8") as file_stream:
            output = json.dumps(content)
            file_stream.writelines(output)

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
            self._write_test_file()

            try:
                # Run the test item
                function(self)
            finally:
                # Delete file finally
                self._delete_file()

        return _
