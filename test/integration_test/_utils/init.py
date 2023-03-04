from pymock_api._utils import load_config
from pymock_api.model import APIConfig

from .._spec import TestSpecWithFileOpt


class TestInitFunctions(TestSpecWithFileOpt):
    @property
    def file_path(self) -> str:
        return "./test.yaml"

    @property
    def not_exist_file_path(self) -> str:
        return "./file_not_exist.yaml"

    @TestSpecWithFileOpt._test_with_file
    def test_load_config(self):
        # Run target function
        loaded_data = load_config(config_path=self.file_path)

        # Verify result
        assert isinstance(loaded_data, APIConfig) and len(loaded_data) != 0, ""
        return "./file_not_exist.yaml"

    @TestSpecWithFileOpt._test_with_file
    def test_load_config_with_not_exist_file(self):
        try:
            # Run target function to test
            load_config(config_path=self.not_exist_file_path)
        except FileNotFoundError as e:
            # Verify result
            expected_err_msg = f"The target configuration file {self.not_exist_file_path} doesn't exist."
            assert str(e) == expected_err_msg, f"The error message should be same as '{expected_err_msg}'."
        else:
            # Verify result
            assert False, "It should raise an exception about 'FileNotFoundError'."
