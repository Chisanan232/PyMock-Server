from typing import Callable
from unittest.mock import MagicMock, mock_open, patch

import pytest
import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from pymock_api._utils.file_opt import YAML


class TestYAMLReader:
    @pytest.fixture(scope="function")
    def yaml_opt(self) -> YAML:
        return YAML()

    @property
    def not_exist_file(self) -> str:
        return "file_not_found.yaml"

    def test_read_with_not_exist_file(self, yaml_opt: YAML):
        # Mock functions
        yaml.load = MagicMock(return_value=None)
        with patch("builtins.open", mock_open(read_data=None)) as mock_file_stream:
            with pytest.raises(FileNotFoundError) as exc_info:
                # Run target function to test
                yaml_opt.read(path=self.not_exist_file)
                # Verify result
                expected_err_msg = f"The target configuration file {self.not_exist_file} doesn't exist."
                assert str(exc_info) == expected_err_msg, f"The error message should be same as '{expected_err_msg}'."
                mock_file_stream.assert_not_called()
                yaml.load.assert_not_called()
