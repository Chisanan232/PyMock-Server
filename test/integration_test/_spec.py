import os
from abc import ABCMeta, abstractmethod

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

    def _delete_file(self) -> None:
        if self._exist_file():
            os.remove(self.file_path)
        exist_file = self._exist_file()
        assert exist_file is False, ""

    def _exist_file(self) -> bool:
        return os.path.exists(self.file_path)

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
