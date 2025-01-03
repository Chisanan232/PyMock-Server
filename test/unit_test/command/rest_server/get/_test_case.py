from typing import List, Union

# isort: off

from test._base_test_case import BaseTestCaseFactory, TestCaseDirPath

# isort: on

# [("yaml_config_path", "get_api_path", "expected_exit_code")]
GET_YAML_PATHS_WITH_EX_CODE: List[tuple] = []


class SubCmdGetTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def test_data_dir(cls) -> TestCaseDirPath:
        return TestCaseDirPath.GET_TEST

    @classmethod
    def get_test_case(cls) -> List[tuple]:
        return GET_YAML_PATHS_WITH_EX_CODE

    @classmethod
    def load(
        cls, get_api_path: str, is_valid_config: bool, exit_code: Union[str, int], acceptable_error: bool = None
    ) -> None:

        def _generate_test_case_callback(file_path: str) -> None:
            expected_exit_code = exit_code if isinstance(exit_code, str) and exit_code.isdigit() else str(exit_code)
            one_test_scenario = (file_path, get_api_path, expected_exit_code)
            GET_YAML_PATHS_WITH_EX_CODE.append(one_test_scenario)

        is_valid_path = "valid" if is_valid_config else "invalid"
        if is_valid_config is False and acceptable_error is not None:
            config_folder = "warn" if acceptable_error else "error"
            entire_config_path = cls.test_data_dir().generate_path_with_base_prefix_path(
                path=(
                    is_valid_path,
                    config_folder,
                    "*.yaml",
                ),
            )
        else:
            entire_config_path = cls.test_data_dir().generate_path_with_base_prefix_path(
                path=(
                    is_valid_path,
                    "*.yaml",
                ),
            )
        cls._iterate_files_by_path(
            path=entire_config_path,
            generate_test_case_callback=_generate_test_case_callback,
        )
