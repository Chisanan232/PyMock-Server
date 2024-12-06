from collections import namedtuple
from typing import List, Tuple

# isort: off
from test._base_test_case import BaseTestCaseFactory, TestCaseDirPath

# isort: on

# [(swagger_api_config_path, cmd_arg, expected_path)]
DIVIDING_YAML_PATHS: List[tuple] = []


SubCmdPullTestArgs = namedtuple(
    "SubCmdPullTestArgs",
    (
        "base_url",
        "include_template_config",
        "divide_api",
        "divide_http",
        "divide_http_request",
        "divide_http_response",
    ),
)


class PullOpenAPIDocConfigAsDividingConfigTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def test_data_dir(cls) -> TestCaseDirPath:
        return TestCaseDirPath.DIVIDE_TEST_PULL

    @classmethod
    def get_test_case(cls) -> List[tuple]:
        return DIVIDING_YAML_PATHS

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

        def _generate_dir_paths_with_v2_openapi_doc(folder_path: str) -> tuple:
            return _generate_dir_paths_by_openapi_version(
                folder_path=folder_path, openapi_doc_config_file="v2_openapi_config.json"
            )

        def _generate_dir_paths_with_v3_openapi_doc(folder_path: str) -> tuple:
            return _generate_dir_paths_by_openapi_version(
                folder_path=folder_path, openapi_doc_config_file="v3_openapi_config.json"
            )

        def _generate_dir_paths_by_openapi_version(folder_path: str, openapi_doc_config_file: str):
            nonlocal test_cmd_opt_arg
            test_cmd_opt_arg = cls._divide_chk(folder_path)
            openapi_config_response = _get_path(scenario_folder=folder_path, yaml_file_naming=openapi_doc_config_file)
            expected_yaml_config = _get_path(scenario_folder=folder_path, yaml_file_naming="expect_config/api.yaml")
            return openapi_config_response, expected_yaml_config

        def _generate_test_case_callback(pair_files: tuple) -> None:
            swagger_api_resp_path = pair_files[0]
            expected_yaml_config_path = pair_files[1]

            if "has_tag" in swagger_api_resp_path:
                base_url = "/api/v1/test"
            else:
                base_url = ""
            if "include_template" in swagger_api_resp_path:
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
            cmd_arg = SubCmdPullTestArgs(**test_cmd_opt_arg)
            one_test_scenario = (swagger_api_resp_path, cmd_arg, expected_yaml_config_path)
            DIVIDING_YAML_PATHS.append(one_test_scenario)

        for generate_dir_paths_callback in (
            _generate_dir_paths_with_v2_openapi_doc,
            _generate_dir_paths_with_v3_openapi_doc,
        ):
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
