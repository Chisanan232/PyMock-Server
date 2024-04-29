from typing import List, Union

from ...._base_test_case import BaseTestCaseFactory, TestCaseDirPath

# [("api_resp_path", "dummy_yaml_path", "stop_if_fail", "expected_exit_code")]
RESPONSE_JSON_PATHS_WITH_EX_CODE: List[tuple] = []
RESPONSE_JSON_PATHS: List[str] = []


class SubCmdCheckComponentTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def get_test_case(cls) -> List[tuple]:
        return RESPONSE_JSON_PATHS_WITH_EX_CODE

    @classmethod
    def load(cls, has_base_info: bool, config_type: str, exit_code: Union[str, int]) -> None:

        test_case_dir = TestCaseDirPath.CHECK_TEST

        def _generate_api_response_in_test_case_callback(json_config_path: str) -> None:

            def _generate_config_in_test_case_callback(yaml_config_path: str) -> None:
                expected_exit_code = exit_code if isinstance(exit_code, str) and exit_code.isdigit() else str(exit_code)
                for stop_if_fail in (True, False):
                    one_test_scenario = (json_config_path, yaml_config_path, stop_if_fail, expected_exit_code)
                    RESPONSE_JSON_PATHS_WITH_EX_CODE.append(one_test_scenario)

            yaml_file_format = "*.yaml" if config_type == "invalid" else f"{file_naming}*.yaml"
            cls._iterate_files_by_path(
                path=(
                    test_case_dir.get_test_source_path(__file__),
                    test_case_dir.base_data_path,
                    test_case_dir.name,
                    "diff_with_swagger",
                    "config",
                    config_type,
                    yaml_file_format,
                ),
                generate_test_case_callback=_generate_config_in_test_case_callback,
            )

        file_naming = "has-base-info" if has_base_info else "no-base-info"
        cls._iterate_files_by_path(
            path=(
                test_case_dir.get_test_source_path(__file__),
                test_case_dir.base_data_path,
                test_case_dir.name,
                "diff_with_swagger",
                "api_response",
                f"{file_naming}*.json",
            ),
            generate_test_case_callback=_generate_api_response_in_test_case_callback,
        )


class SwaggerDiffCheckTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def get_test_case(cls) -> List[str]:
        return RESPONSE_JSON_PATHS

    @classmethod
    def load(cls) -> None:

        def _generate_test_case_callback(file_path: str) -> None:
            one_test_scenario = file_path
            global RESPONSE_JSON_PATHS
            RESPONSE_JSON_PATHS.append(one_test_scenario)

        test_case_dir = TestCaseDirPath.CHECK_TEST
        cls._iterate_files_by_path(
            path=test_case_dir.generate_path_with_base_prefix_path(
                current_file=__file__,
                path=(
                    "diff_with_swagger",
                    "api_response",
                    "*.json",
                ),
            ),
            generate_test_case_callback=_generate_test_case_callback,
        )
