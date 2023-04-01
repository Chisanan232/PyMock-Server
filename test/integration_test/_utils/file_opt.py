import os

import pytest

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

from pymock_api._utils.file_opt import YAML

from ..._values import _Test_Config_Value
from .._spec import MockAPI_Config_Path, run_test


class TestYAML:

    _Test_File: str = "pytest-yaml-write.yaml"

    @pytest.fixture(scope="function")
    def yaml_opt(self) -> YAML:
        self._remove_test_config()
        return YAML()

    @run_test.with_file
    def test_open_and_read(self, yaml_opt: YAML):
        # Run target function
        reading_data = yaml_opt.read(path=MockAPI_Config_Path)

        # Verify result
        assert reading_data and isinstance(reading_data, dict)
        assert reading_data == _Test_Config_Value

    def test_write(self, yaml_opt: YAML):
        try:
            assert os.path.exists(self._Test_File) is False
            config_data = yaml_opt.serialize(config=_Test_Config_Value)
            yaml_opt.write(path=self._Test_File, config=config_data)

            assert isinstance(config_data, str)
            assert os.path.exists(self._Test_File)
            config = yaml_opt.read(self._Test_File)
            assert config == _Test_Config_Value
        finally:
            self._remove_test_config()

    def _remove_test_config(self):
        if os.path.exists(self._Test_File):
            os.remove(self._Test_File)
