import glob
import os
import pathlib
from collections import namedtuple
from typing import List

from ...._base_test_case import BaseTestCaseFactory

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
    def get_test_case(cls) -> List[tuple]:
        return DIVIDING_YAML_PATHS

    @classmethod
    def load(cls) -> None:
        def _get_path(scenario_folder: str = "", yaml_file_naming: str = "") -> str:
            _path = (
                str(pathlib.Path(__file__).parent.parent.parent.parent),
                "data",
                "divide_test_pull",
                scenario_folder,
                yaml_file_naming,
            )
            return os.path.join(*_path)

        different_scenarios_data_folder = os.listdir(_get_path())
        for f in different_scenarios_data_folder:
            test_cmd_opt_arg = cls._divide_chk(f)
            swagger_api = _get_path(scenario_folder=f, yaml_file_naming="swagger_api.json")
            expected_yaml_dir = _get_path(scenario_folder=f, yaml_file_naming="expect_config/api.yaml")
            global DIVIDING_YAML_PATHS
            for swagger_api_resp_path, expected_yaml_config_path in zip(
                glob.glob(swagger_api), glob.glob(expected_yaml_dir)
            ):
                if "has_tag" in swagger_api_resp_path:
                    base_url = "/api/v1/test"
                else:
                    base_url = ""
                if "include_template" in swagger_api_resp_path:
                    include_template_config = True
                else:
                    include_template_config = False
                test_cmd_opt_arg.update(
                    {
                        "base_url": base_url,
                        "include_template_config": include_template_config,
                    }
                )
                cmd_arg = SubCmdPullTestArgs(**test_cmd_opt_arg)
                one_test_scenario = (swagger_api_resp_path, cmd_arg, expected_yaml_config_path)
                DIVIDING_YAML_PATHS.append(one_test_scenario)

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
