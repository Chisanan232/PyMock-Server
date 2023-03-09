import pytest

from pymock_api._utils import load_config
from pymock_api.model import APIConfig

from .._spec import SpecWithFileOpt


class TestInitFunctions(SpecWithFileOpt):
    @property
    def file_path(self) -> str:
        return "./test.yaml"

    @property
    def not_exist_file_path(self) -> str:
        return "./file_not_exist.yaml"

    @SpecWithFileOpt._test_with_file
    def test_load_config(self):
        # Run target function
        loaded_data = load_config(config_path=self.file_path)

        # Verify result
        assert isinstance(loaded_data, APIConfig) and len(loaded_data) != 0, ""
        return "./file_not_exist.yaml"

    @SpecWithFileOpt._test_with_file
    def test_load_config_with_not_exist_file(self):
        with pytest.raises(FileNotFoundError) as exc_info:
            # Run target function to test
            load_config(config_path=self.not_exist_file_path)
            # Verify result
            expected_err_msg = f"The target configuration file {self.not_exist_file_path} doesn't exist."
            assert str(exc_info) == expected_err_msg, f"The error message should be same as '{expected_err_msg}'."
