import os

import pytest

from .._spec import MockAPI_Config_Path, run_test

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

from pymock_api._utils.reader import YAMLReader, YAMLWriter
from pymock_api.model.api_config import APIConfig

from ..._values import _Test_Config_Value


class TestYAMLReader:
    @pytest.fixture(scope="function")
    def reader(self) -> YAMLReader:
        return YAMLReader()

    @run_test.with_file
    def test_open_and_read(self, reader: YAMLReader):
        # Run target function
        reading_data = reader.read(config=MockAPI_Config_Path)

        # Verify result
        assert isinstance(reading_data, dict) and len(reading_data) != 0, ""
        assert reading_data == _Test_Config_Value, ""

    def test_deserialize(self, reader: YAMLReader):
        # Run target function
        deserialized_data = reader.deserialize(data=_Test_Config_Value)

        # Verify result
        assert isinstance(deserialized_data, APIConfig) and len(deserialized_data) != 0, ""

    @run_test.with_file
    def test_load(self, reader: YAMLReader):
        # Run target function
        loaded_data = reader.load(config=MockAPI_Config_Path)

        # Verify result
        assert isinstance(loaded_data, APIConfig) and len(loaded_data) != 0, ""


class TestYAMLWriter:

    _Test_File: str = "pytest-yaml-write.yaml"

    @pytest.fixture(scope="function")
    def writer(self) -> YAMLWriter:
        self._remove_test_config()
        return YAMLWriter()

    def test_write(self, writer: YAMLWriter):
        try:
            assert os.path.exists(self._Test_File) is False
            config_data = writer.serialize(config=_Test_Config_Value)
            writer.write(path=self._Test_File, config=config_data)

            assert isinstance(config_data, str)
            assert os.path.exists(self._Test_File)
            config = YAMLReader().load(self._Test_File)
            assert isinstance(config, APIConfig) and len(config) != 0, ""
            for api_name, api_config in config.apis.apis.items():
                assert api_name in _Test_Config_Value["mocked_apis"].keys()
        finally:
            self._remove_test_config()

    def _remove_test_config(self):
        if os.path.exists(self._Test_File):
            os.remove(self._Test_File)
