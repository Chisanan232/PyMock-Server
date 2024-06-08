from collections import namedtuple
from typing import List, Tuple

from ...._base_test_case import BaseTestCaseFactory, TestCaseDirPath

# [(swagger_api_config_path, cmd_arg, expected_path)]
ADD_AS_DIVIDING_YAML_PATHS: List[tuple] = []


SubCmdAddTestArgs = namedtuple(
    "SubCmdAddTestArgs",
    (
        "base_url",
        "include_template_config",
        "divide_api",
        "divide_http",
        "divide_http_request",
        "divide_http_response",
    ),
)


class AddMockAPIAsDividingConfigTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def test_data_dir(cls) -> TestCaseDirPath:
        return TestCaseDirPath.ADD_TEST

    @classmethod
    def get_test_case(cls) -> List[tuple]:
        return ADD_AS_DIVIDING_YAML_PATHS

    @classmethod
    def load(cls) -> None:
        test_cmd_opt_arg: dict = {}

        def _get_path(scenario_folder: str = "", yaml_file_naming: str = "") -> Tuple:
            return cls.test_data_dir().generate_path_with_base_prefix_path(
                path=(
                    scenario_folder,
                    yaml_file_naming,
                ),
            )

        def generate_dir_paths_callback(folder_path: str) -> tuple:
            nonlocal test_cmd_opt_arg
            test_cmd_opt_arg = cls._divide_chk(folder_path)
            new_config_has_new_api = _get_path(scenario_folder=folder_path, yaml_file_naming="add_test")
            expected_yaml_config = _get_path(scenario_folder=folder_path, yaml_file_naming="expect_config/api.yaml")
            return new_config_has_new_api, expected_yaml_config

        def _generate_test_case_callback(pair_files: tuple) -> None:
            new_config_path_has_new_api = pair_files[0]
            expected_yaml_config_path = pair_files[1]

            if "has_tag" in new_config_path_has_new_api:
                base_url = "/api/v1/test"
            else:
                base_url = ""
            if "include_template" in new_config_path_has_new_api:
                include_template_config = True
            else:
                include_template_config = False
            nonlocal test_cmd_opt_arg
            assert test_cmd_opt_arg
            test_cmd_opt_arg.update(
                {
                    "base_url": base_url,
                    "include_template_config": include_template_config,
                }
            )
            cmd_arg = SubCmdAddTestArgs(**test_cmd_opt_arg)
            one_test_scenario = (new_config_path_has_new_api, cmd_arg, expected_yaml_config_path)
            print(f"[DEBUG in general] one_test_scenario: {one_test_scenario}")
            ADD_AS_DIVIDING_YAML_PATHS.append(one_test_scenario)

        cls._iterate_files_by_directory(
            path=_get_path(),
            generate_dir_paths=generate_dir_paths_callback,
            generate_test_case_callback=_generate_test_case_callback,
        )

    @classmethod
    def _divide_chk(cls, test_scenario_dir: str) -> dict:
        cmd_divide_arg = {
            "divide_api": False,
            "divide_http": False,
            "divide_http_request": False,
            "divide_http_response": False,
        }

        def _set_val(key: str, cmd_key: str = "") -> None:
            if key in test_scenario_dir:
                cmd_divide_key = cmd_key if cmd_key else key
                cmd_divide_arg[f"divide_{cmd_divide_key}"] = True

        _set_val("api")
        _set_val("http")
        _set_val("request", "http_request")
        _set_val("response", "http_response")

        return cmd_divide_arg
