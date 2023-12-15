import glob
import json
import os
import pathlib
from collections import namedtuple
from typing import List
from unittest.mock import PropertyMock, patch

import pytest

from pymock_api.command.options import SubCommand
from pymock_api.command.pull.component import SubCmdPullComponent
from pymock_api.model import SubcmdPullArguments, load_config
from pymock_api.model.api_config import TemplateConfig
from pymock_api.model.swagger_config import set_component_definition

from ...._values import _API_Doc_Source, _Test_Request_With_Https

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


def _get_all_yaml_for_dividing() -> None:
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
        test_cmd_opt_arg = _divide_chk(f)
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


def _divide_chk(test_scenario_dir: str) -> dict:
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


_get_all_yaml_for_dividing()


class TestSubCmdPullComponent:
    @pytest.fixture(scope="function")
    def sub_cmd(self) -> SubCmdPullComponent:
        return SubCmdPullComponent()

    @pytest.mark.parametrize(("swagger_api_resp_path", "cmd_arg", "expected_yaml_config_path"), DIVIDING_YAML_PATHS)
    def test_pull_swagger_api_as_dividing_config(
        self,
        swagger_api_resp_path: str,
        cmd_arg: SubCmdPullTestArgs,
        expected_yaml_config_path: str,
        sub_cmd: SubCmdPullComponent,
    ):
        # Given command line argument
        print(f"[DEBUG in test] cmd_arg: {cmd_arg}")
        test_scenario_dir = pathlib.Path(swagger_api_resp_path).parent
        ut_dir = pathlib.Path(test_scenario_dir, "under_test")
        if not ut_dir.exists():
            ut_dir.mkdir()
        ut_config_path = str(pathlib.Path(ut_dir, "api.yaml"))
        cmd_args = SubcmdPullArguments(
            subparser_name=SubCommand.Pull,
            request_with_https=_Test_Request_With_Https,
            source=_API_Doc_Source,
            config_path=ut_config_path,
            base_url=cmd_arg.base_url,
            include_template_config=cmd_arg.include_template_config,
            base_file_path=str(ut_dir),
            dry_run=False,
            divide_api=cmd_arg.divide_api,
            divide_http=cmd_arg.divide_http,
            divide_http_request=cmd_arg.divide_http_request,
            divide_http_response=cmd_arg.divide_http_response,
        )

        with open(swagger_api_resp_path, "r") as file:
            swagger_api_resp = json.loads(file.read())

        with patch(
            "pymock_api.model.api_config.MockAPIs.template", new_callable=PropertyMock
        ) as mock_mock_apis_template:
            template_config = TemplateConfig()
            # Set the base file path to let the test could run and save the result configuration under the target
            # directory
            template_config.values.base_file_path = str(ut_dir)
            mock_mock_apis_template.return_value = template_config

            # Set the Swagger API reference data for testing
            set_component_definition(swagger_api_resp)
            # Mock the HTTP request result as the Swagger API documentation data
            with patch(
                "pymock_api.command.pull.component.URLLibHTTPClient.request", return_value=swagger_api_resp
            ) as mock_swagger_request:
                # Run target function
                sub_cmd.process(args=cmd_args)

                # Expected values
                expected_config_data_modal = load_config(expected_yaml_config_path, is_pull=True)

                # Verify
                mock_swagger_request.assert_called_once()
                ut_config_data_modal = load_config(ut_config_path, is_pull=True)
                assert ut_config_data_modal is not None
                assert expected_config_data_modal is not None

                # Basic configuration
                assert ut_config_data_modal.name == expected_config_data_modal.name
                assert ut_config_data_modal.description == expected_config_data_modal.description

                # mock APIs configuration
                assert ut_config_data_modal.apis is not None
                assert expected_config_data_modal.apis is not None
                assert ut_config_data_modal.apis.base == expected_config_data_modal.apis.base
                assert ut_config_data_modal.apis.apis.keys() == expected_config_data_modal.apis.apis.keys()
                for api_key in expected_config_data_modal.apis.apis.keys():
                    ut_api = ut_config_data_modal.apis.apis[api_key]
                    expect_api = expected_config_data_modal.apis.apis[api_key]

                    # Basic checking
                    assert ut_api is not None
                    assert expect_api is not None
                    assert ut_api.http is not None
                    assert expect_api.http is not None

                    # Details checking
                    assert ut_api.url == expect_api.url
                    assert ut_api.tag == expect_api.tag
                    assert ut_api.http.request == expect_api.http.request
                    assert ut_api.http.response == expect_api.http.response
