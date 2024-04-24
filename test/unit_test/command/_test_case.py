import glob
import os
import pathlib
from typing import List, Union

GET_YAML_PATHS_WITH_EX_CODE: List[tuple] = []


def _get_all_yaml_for_subcmd_get(
    get_api_path: str, is_valid_config: bool, exit_code: Union[str, int], acceptable_error: bool = None
) -> None:
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
    yaml_dir = os.path.join(*entire_config_path)
    global GET_YAML_PATHS_WITH_EX_CODE
    for yaml_config_path in glob.glob(yaml_dir):
        expected_exit_code = exit_code if isinstance(exit_code, str) and exit_code.isdigit() else str(exit_code)
        one_test_scenario = (yaml_config_path, get_api_path, expected_exit_code)
        GET_YAML_PATHS_WITH_EX_CODE.append(one_test_scenario)


PULL_YAML_PATHS_WITH_CONFIG: List[tuple] = []


def _get_all_yaml_for_subcmd_pull() -> None:
    def _get_path(data_type: str, file_extension: str) -> str:
        return os.path.join(
            str(pathlib.Path(__file__).parent.parent.parent),
            "data",
            "pull_test",
            data_type,
            f"*.{file_extension}",
        )

    config_yaml_path = _get_path("config", "yaml")
    swagger_json_path = _get_path("swagger", "json")

    global PULL_YAML_PATHS_WITH_CONFIG
    for yaml_config_path, json_path in zip(sorted(glob.glob(config_yaml_path)), sorted(glob.glob(swagger_json_path))):
        for dry_run_scenario in (True, False):
            one_test_scenario = (json_path, dry_run_scenario, yaml_config_path)
            PULL_YAML_PATHS_WITH_CONFIG.append(one_test_scenario)
