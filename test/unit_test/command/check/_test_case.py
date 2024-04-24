import glob
import os
import pathlib
from typing import List, Union

RESPONSE_JSON_PATHS_WITH_EX_CODE: List[tuple] = []
RESPONSE_JSON_PATHS: List[str] = []


def _get_all_json(has_base_info: bool, config_type: str, exit_code: Union[str, int]) -> None:
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


def _get_all_swagger_config() -> None:
    json_dir = os.path.join(
        str(pathlib.Path(__file__).parent.parent.parent.parent),
        "data",
        "check_test",
        "diff_with_swagger",
        "api_response",
        "*.json",
    )
    global RESPONSE_JSON_PATHS
    for json_config_path in glob.glob(json_dir):
        one_test_scenario = json_config_path
        RESPONSE_JSON_PATHS.append(one_test_scenario)
