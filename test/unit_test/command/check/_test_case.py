import glob
import os
import pathlib
from typing import Callable, List, Union

from ...._base_test_case import BaseTestCaseFactory

# [("api_resp_path", "dummy_yaml_path", "stop_if_fail", "expected_exit_code")]
RESPONSE_JSON_PATHS_WITH_EX_CODE: List[tuple] = []
RESPONSE_JSON_PATHS: List[str] = []


class SubCmdCheckComponentTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def get_test_case(cls) -> List[tuple]:
        return RESPONSE_JSON_PATHS_WITH_EX_CODE

    @classmethod
    def load(cls, has_base_info: bool, config_type: str, exit_code: Union[str, int]) -> None:
        file_naming = "has-base-info" if has_base_info else "no-base-info"
        json_dir = os.path.join(
            str(pathlib.Path(__file__).parent.parent.parent.parent),
            "data",
            "check_test",
            "diff_with_swagger",
            "api_response",
            f"{file_naming}*.json",
        )
        global RESPONSE_JSON_PATHS_WITH_EX_CODE
        for json_config_path in glob.glob(json_dir):
            yaml_file_format = "*.yaml" if config_type == "invalid" else f"{file_naming}*.yaml"
            yaml_dir = os.path.join(
                str(pathlib.Path(__file__).parent.parent.parent.parent),
                "data",
                "check_test",
                "diff_with_swagger",
                "config",
                config_type,
                yaml_file_format,
            )
            expected_exit_code = exit_code if isinstance(exit_code, str) and exit_code.isdigit() else str(exit_code)
            for yaml_config_path in glob.glob(yaml_dir):
                for stop_if_fail in (True, False):
                    one_test_scenario = (json_config_path, yaml_config_path, stop_if_fail, expected_exit_code)
                    RESPONSE_JSON_PATHS_WITH_EX_CODE.append(one_test_scenario)


class SwaggerDiffCheckTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def get_test_case(cls) -> List[str]:
        return RESPONSE_JSON_PATHS

    @classmethod
    def load(cls) -> None:

        def _generate_test_case_callback(json_config_path: str) -> None:
            one_test_scenario = json_config_path
            global RESPONSE_JSON_PATHS
            RESPONSE_JSON_PATHS.append(one_test_scenario)

        cls._iterate_files_by_path(_generate_test_case_callback)

    @classmethod
    def _iterate_files_by_path(cls, _generate_test_case_callback: Callable) -> None:
        json_dir = os.path.join(
            str(pathlib.Path(__file__).parent.parent.parent.parent),
            "data",
            "check_test",
            "diff_with_swagger",
            "api_response",
            "*.json",
        )
        for json_config_path in glob.glob(json_dir):
            _generate_test_case_callback(json_config_path)
