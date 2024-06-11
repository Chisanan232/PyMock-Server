import pathlib
from collections import namedtuple
from typing import List, Tuple

from pymock_api.model.enums import ResponseStrategy

from ...._base_test_case import BaseTestCaseFactory, TestCaseDirPath
from ...._values import _generate_response_for_add, _Test_Tag

# [(swagger_api_config_path, cmd_arg, expected_path)]
ADD_AS_DIVIDING_YAML_PATHS: List[tuple] = []


SubCmdAddTestArgs = namedtuple(
    "SubCmdAddTestArgs",
    (
        "base_url",
        "include_template_config",
        "tag",
        "divide_api",
        "divide_http",
        "divide_http_request",
        "divide_http_response",
        # response setting
        "resp_strategy",
        "resp_details",
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
            divide_arg = cls._divide_chk(folder_path)
            resp_args = cls._resp_chk(folder_path)
            test_cmd_opt_arg.update(divide_arg)
            test_cmd_opt_arg.update(resp_args)
            expected_yaml_config = _get_path(scenario_folder=folder_path, yaml_file_naming="expect_config/api.yaml")
            return (expected_yaml_config,)

        def _generate_test_case_callback(pair_files: tuple) -> None:
            expected_yaml_config_path = pair_files[0]

            if "has_tag" in expected_yaml_config_path:
                base_url = "/api/v1/test"
                tag = _Test_Tag
            else:
                base_url = ""
                tag = ""
            if "include_template" in expected_yaml_config_path:
                include_template_config = True
            else:
                include_template_config = False
            nonlocal test_cmd_opt_arg
            assert test_cmd_opt_arg
            test_cmd_opt_arg.update(
                {
                    "base_url": base_url,
                    "include_template_config": include_template_config,
                    "tag": tag,
                }
            )
            cmd_arg = SubCmdAddTestArgs(**test_cmd_opt_arg)
            under_test_dir = pathlib.Path(pathlib.Path(expected_yaml_config_path).parent.parent, "under_test")
            one_test_scenario = (under_test_dir, cmd_arg, expected_yaml_config_path)
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

    @classmethod
    def _resp_chk(cls, test_scenario_dir: str):
        resp_arg = {}

        if "string_strategy_resp" in test_scenario_dir:
            strategy, resp_setting = _generate_response_for_add(ResponseStrategy.STRING)
        elif "object_strategy_resp" in test_scenario_dir:
            strategy, resp_setting = _generate_response_for_add(ResponseStrategy.OBJECT)
        else:
            raise ValueError("Not support this test criteria. Please check it.")

        resp_arg["resp_strategy"] = strategy
        resp_arg["resp_details"] = resp_setting  # type: ignore[assignment]
        return resp_arg
