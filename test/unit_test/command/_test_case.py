import os
import pathlib
from typing import List, Union

from ..._base_test_case import BaseTestCaseFactory

# [("yaml_config_path", "get_api_path", "expected_exit_code")]
GET_YAML_PATHS_WITH_EX_CODE: List[tuple] = []


class SubCmdGetTestCaseFactory(BaseTestCaseFactory):

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
            entire_config_path = (
                str(pathlib.Path(__file__).parent.parent.parent),
                "data",
                "get_test",
                is_valid_path,
                config_folder,
                "*.yaml",
            )
        else:
            entire_config_path = (
                str(pathlib.Path(__file__).parent.parent.parent),
                "data",
                "get_test",
                is_valid_path,
                "*.yaml",
            )
        cls._iterate_files_by_path(
            path=entire_config_path,
            generate_test_case_callback=_generate_test_case_callback,
        )


# [("swagger_config", "dry_run", "expected_config")]
PULL_YAML_PATHS_WITH_CONFIG: List[tuple] = []


class SubCmdPullTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def get_test_case(cls) -> List[tuple]:
        return PULL_YAML_PATHS_WITH_CONFIG

    @classmethod
    def load(cls) -> None:
        def _get_path(data_type: str, file_extension: str) -> str:
            return os.path.join(
                str(pathlib.Path(__file__).parent.parent.parent),
                "data",
                "pull_test",
                data_type,
                f"*.{file_extension}",
            )

        def _generate_test_case_callback(pair_paths: tuple) -> None:
            yaml_config_path = pair_paths[0]
            json_path = pair_paths[1]
            for dry_run_scenario in (True, False):
                one_test_scenario = (json_path, dry_run_scenario, yaml_config_path)
                PULL_YAML_PATHS_WITH_CONFIG.append(one_test_scenario)

        config_yaml_path = _get_path("config", "yaml")
        swagger_json_path = _get_path("swagger", "json")

        cls._iterate_files_by_paths(
            paths=(config_yaml_path, swagger_json_path),
            generate_test_case_callback=_generate_test_case_callback,
            sort=True,
        )
