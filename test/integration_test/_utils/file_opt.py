import os
from abc import ABCMeta, abstractmethod

import pytest

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper  # type: ignore

from pymock_api._utils.file_opt import YAML, _BaseFileOperation

from ..._values import _Test_Config_Value
from .._spec import MockAPI_Config_Yaml_Path, run_test, yaml_factory


class _BaseTestSuite(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    def file_opt(self) -> _BaseFileOperation:
        self._remove_test_config()
        return self._under_test_object()

    @property
    @abstractmethod
    def _file_path(self) -> str:
        pass

    @abstractmethod
    def _under_test_object(self) -> _BaseFileOperation:
        pass

    @run_test.with_file(yaml_factory)
    def test_open_and_read(self, file_opt: _BaseFileOperation):
        # Run target function
        reading_data = file_opt.read(path=MockAPI_Config_Yaml_Path)

        # Verify result
        assert reading_data and isinstance(reading_data, dict)
        assert reading_data == _Test_Config_Value

    def test_write(self, file_opt: _BaseFileOperation):
        try:
            assert os.path.exists(self._file_path) is False
            config_data = file_opt.serialize(config=_Test_Config_Value)
            file_opt.write(path=self._file_path, config=config_data)

            assert isinstance(config_data, str)
            assert os.path.exists(self._file_path)
            config = file_opt.read(self._file_path)
            assert config == _Test_Config_Value
        finally:
            self._remove_test_config()

    def _remove_test_config(self):
        if os.path.exists(self._file_path):
            os.remove(self._file_path)


class TestYAML(_BaseTestSuite):
    def _under_test_object(self) -> YAML:
        return YAML()

    @property
    def _file_path(self) -> str:
        return "pytest-yaml-write.yaml"
