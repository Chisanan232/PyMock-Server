from typing import Callable
from unittest.mock import MagicMock, mock_open, patch

import pytest
import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from pymock_api._utils.reader import YAMLReader


class TestYAMLReader:
    @pytest.fixture(scope="function")
    def reader(self) -> YAMLReader:
        return YAMLReader()

    @property
    def not_exist_file(self) -> str:
        return "file_not_found.yaml"

    def test_read_with_not_exist_file(self, reader: YAMLReader):
        self._template_test_raise_file_not_found_error(
            reader=reader, target_test=reader.read, target_test_args={"config": self.not_exist_file}
        )

    def test_load_with_not_exist_file(self, reader: YAMLReader):
        self._template_test_raise_file_not_found_error(
            reader=reader, target_test=reader.load, target_test_args={"config": self.not_exist_file}
        )

    def _template_test_raise_file_not_found_error(
        self, reader: YAMLReader, target_test: Callable, target_test_args: dict
    ) -> None:
        # Mock functions
        yaml.load = MagicMock(return_value=None)

        with patch("builtins.open", mock_open(read_data=None)) as mock_file_stream:
            try:
                # Run target function to test
                target_test(**target_test_args)
            except FileNotFoundError as e:
                # Verify result
                expected_err_msg = f"The target configuration file {self.not_exist_file} doesn't exist."
                assert str(e) == expected_err_msg, f"The error message should be same as '{expected_err_msg}'."
                mock_file_stream.assert_not_called()
                yaml.load.assert_not_called()
            else:
                # Verify result
                assert False, "It should raise an exception about 'FileNotFoundError'."
