from test._base_test_case import BaseTestCaseFactory, TestCaseDirPath
from typing import List, Union

# [("api_resp_path", "dummy_yaml_path", "stop_if_fail", "expected_exit_code")]
RESPONSE_JSON_PATHS_WITH_EX_CODE: List[tuple] = []
RESPONSE_JSON_PATHS: List[str] = []


class SubCmdCheckComponentTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def test_data_dir(cls) -> TestCaseDirPath:
        return TestCaseDirPath.CHECK_TEST

    @classmethod
    def get_test_case(cls) -> List[tuple]:
        return RESPONSE_JSON_PATHS_WITH_EX_CODE

    @classmethod
    def load(cls, has_base_info: bool, config_type: str, exit_code: Union[str, int]) -> None:

        def _generate_api_response_in_test_case_callback(json_config_path: str) -> None:

            def _generate_config_in_test_case_callback(yaml_config_path: str) -> None:
                expected_exit_code = exit_code if isinstance(exit_code, str) and exit_code.isdigit() else str(exit_code)
                for stop_if_fail in (True, False):
                    one_test_scenario = (json_config_path, yaml_config_path, stop_if_fail, expected_exit_code)
                    RESPONSE_JSON_PATHS_WITH_EX_CODE.append(one_test_scenario)

            yaml_file_format = "*.yaml" if config_type == "invalid" else f"{file_naming}*.yaml"
            cls._iterate_files_by_path(
                path=cls.test_data_dir().generate_path_with_base_prefix_path(
                    path=(
                        "diff_with_swagger",
                        "config",
                        config_type,
                        yaml_file_format,
                    ),
                ),
                generate_test_case_callback=_generate_config_in_test_case_callback,
            )

        file_naming = "has-base-info" if has_base_info else "no-base-info"
        cls._iterate_files_by_path(
            path=cls.test_data_dir().generate_path_with_base_prefix_path(
                path=(
                    "diff_with_swagger",
                    "openapi_config",
                    "version3",
                    f"{file_naming}*.json",
                ),
            ),
            generate_test_case_callback=_generate_api_response_in_test_case_callback,
        )


class SwaggerDiffCheckTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def test_data_dir(cls) -> TestCaseDirPath:
        return TestCaseDirPath.CHECK_TEST

    @classmethod
    def get_test_case(cls) -> List[str]:
        return RESPONSE_JSON_PATHS

    @classmethod
    def load(cls) -> None:

        def _generate_test_case_callback(file_path: str) -> None:
            one_test_scenario = file_path
            global RESPONSE_JSON_PATHS
            RESPONSE_JSON_PATHS.append(one_test_scenario)

        cls._iterate_files_by_path(
            path=cls.test_data_dir().generate_path_with_base_prefix_path(
                path=(
                    "diff_with_swagger",
                    "openapi_config",
                    "version3",
                    "*.json",
                ),
            ),
            generate_test_case_callback=_generate_test_case_callback,
        )
