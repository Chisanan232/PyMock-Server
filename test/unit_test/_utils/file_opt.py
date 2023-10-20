from abc import ABCMeta, abstractmethod
from unittest.mock import mock_open, patch

import pytest

try:
    pass
except ImportError:
    pass

from pymock_api._utils.file_opt import JSON, YAML, _BaseFileOperation


class _FileOptTestSpec(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def file_opt(self) -> _BaseFileOperation:
        pass

    @property
    @abstractmethod
    def not_exist_file(self) -> str:
        pass

    def test_read_with_not_exist_file(self, file_opt: _BaseFileOperation):
        # Mock functions
        with patch(self._load_function_path, return_value=None) as mock_load:
            with patch("builtins.open", mock_open(read_data=None)) as mock_file_stream:
                with pytest.raises(FileNotFoundError) as exc_info:
                    # Run target function to test
                    file_opt.read(path=self.not_exist_file)
                # Verify result
                expected_err_msg = f"The target configuration file {self.not_exist_file} doesn't exist."
                assert (
                    str(exc_info.value) == expected_err_msg
                ), f"The error message should be same as '{expected_err_msg}'."
                mock_file_stream.assert_not_called()
                mock_load.assert_not_called()

    @property
    @abstractmethod
    def _load_function_path(self) -> str:
        pass


class TestYAML(_FileOptTestSpec):
    @pytest.fixture(scope="function")
    def file_opt(self) -> YAML:
        return YAML()

    @property
    def not_exist_file(self) -> str:
        return "file_not_found.yaml"

    @property
    def _load_function_path(self) -> str:
        return "pymock_api._utils.file_opt.load"


class TestJSON(_FileOptTestSpec):
    @pytest.fixture(scope="function")
    def file_opt(self) -> JSON:
        return JSON()

    @property
    def not_exist_file(self) -> str:
        return "file_not_found.json"

    @property
    def _load_function_path(self) -> str:
        return "pymock_api._utils.file_opt.json.loads"
