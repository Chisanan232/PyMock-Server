from abc import ABCMeta, abstractmethod
from unittest.mock import MagicMock, mock_open, patch

import pytest
import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from pymock_api._utils.file_opt import YAML, _BaseFileOperation


class _FileOptTestSpec(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def file_opt(self) -> _BaseFileOperation:
        pass

    @property
    def not_exist_file(self) -> str:
        return "file_not_found.yaml"

    def test_read_with_not_exist_file(self, file_opt: _BaseFileOperation):
        # Mock functions
        self._mock_load()
        with patch("builtins.open", mock_open(read_data=None)) as mock_file_stream:
            with pytest.raises(FileNotFoundError) as exc_info:
                # Run target function to test
                file_opt.read(path=self.not_exist_file)
                # Verify result
                expected_err_msg = f"The target configuration file {self.not_exist_file} doesn't exist."
                assert str(exc_info) == expected_err_msg, f"The error message should be same as '{expected_err_msg}'."
                mock_file_stream.assert_not_called()
                self._should_call_load()

    @abstractmethod
    def _mock_load(self) -> None:
        pass

    @abstractmethod
    def _should_call_load(self) -> None:
        pass


class TestYAML(_FileOptTestSpec):
    @pytest.fixture(scope="function")
    def file_opt(self) -> YAML:
        return YAML()

    def _mock_load(self) -> None:
        yaml.load = MagicMock(return_value=None)

    def _should_call_load(self) -> None:
        assert isinstance(yaml.load, MagicMock), "The function should be annotated as *MagicMock* type."
        yaml.load.assert_not_called()
