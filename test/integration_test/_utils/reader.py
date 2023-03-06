from abc import ABC

import pytest

from .._spec import SpecWithFileOpt

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

from pymock_api._utils.reader import YAMLReader
from pymock_api.model.api_config import APIConfig

from ..._values import _Test_Config_Value


class ReaderTestSpec(SpecWithFileOpt, ABC):
    @staticmethod
    def _test_with_file(function):
        def _(self, reader):
            # Ensure that it doesn't have file
            self._delete_file()
            # Create the target file before run test
            self._write_test_file()

            try:
                # Run the test item
                function(self, reader)
            finally:
                # Delete file finally
                self._delete_file()

        return _


class TestYAMLReader(ReaderTestSpec):
    @pytest.fixture(scope="function")
    def reader(self) -> YAMLReader:
        return YAMLReader()

    @property
    def file_path(self) -> str:
        return "./test.yaml"

    @ReaderTestSpec._test_with_file
    def test_open_and_read(self, reader: YAMLReader):
        # Run target function
        reading_data = reader.read(config=self.file_path)

        # Verify result
        assert isinstance(reading_data, dict) and len(reading_data) != 0, ""
        assert reading_data == _Test_Config_Value, ""

    def test_deserialize(self, reader: YAMLReader):
        # Run target function
        deserialized_data = reader.deserialize(data=_Test_Config_Value)

        # Verify result
        assert isinstance(deserialized_data, APIConfig) and len(deserialized_data) != 0, ""

    @ReaderTestSpec._test_with_file
    def test_load(self, reader: YAMLReader):
        # Run target function
        loaded_data = reader.load(config=self.file_path)

        # Verify result
        assert isinstance(loaded_data, APIConfig) and len(loaded_data) != 0, ""
