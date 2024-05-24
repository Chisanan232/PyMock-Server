import os
from typing import List, Union

from ..._base_test_case import BaseTestCaseFactory, TestCaseDirPath

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


# [("swagger_config", "dry_run", "expected_config")]
PULL_YAML_PATHS_WITH_CONFIG: List[tuple] = []


class SubCmdPullTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def test_data_dir(cls) -> TestCaseDirPath:
        return TestCaseDirPath.PULL_TEST

    @classmethod
    def get_test_case(cls) -> List[tuple]:
        return PULL_YAML_PATHS_WITH_CONFIG

    @classmethod
    def load(cls) -> None:
        def _get_path(data_type: tuple, file_extension: str) -> str:
            path = cls.test_data_dir().generate_path_with_base_prefix_path(
                path=(
                    *data_type,
                    f"*.{file_extension}",
                ),
            )
            return str(os.path.join(*path))

        def _generate_test_case_callback(pair_paths: tuple) -> None:
            yaml_config_path = pair_paths[0]
            json_path = pair_paths[1]
            for dry_run_scenario in (True, False):
                one_test_scenario = (json_path, dry_run_scenario, yaml_config_path)
                PULL_YAML_PATHS_WITH_CONFIG.append(one_test_scenario)

        from_v2_config_yaml_path = _get_path(("config", "from_v2_openapi"), "yaml")
        from_v3_config_yaml_path = _get_path(("config", "from_v3_openapi"), "yaml")
        v2_openapi_doc_json_path = _get_path(("openapi_doc", "version2"), "json")
        v3_openapi_doc_json_path = _get_path(("openapi_doc", "version3"), "json")

        cls._iterate_files_by_paths(
            paths=(from_v2_config_yaml_path, v2_openapi_doc_json_path),
            generate_test_case_callback=_generate_test_case_callback,
            sort=True,
        )

        cls._iterate_files_by_paths(
            paths=(from_v3_config_yaml_path, v3_openapi_doc_json_path),
            generate_test_case_callback=_generate_test_case_callback,
            sort=True,
        )
