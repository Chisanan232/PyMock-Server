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
            cmd_arg = SubCmdPullTestArgs(base_url=base_url, include_template_config=include_template_config)
            one_test_scenario = (swagger_api_resp_path, cmd_arg, expected_yaml_config_path)
            DIVIDING_YAML_PATHS.append(one_test_scenario)


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
            divide_api=True,
            divide_http=False,
            divide_http_request=False,
            divide_http_response=False,
        )

        with open(swagger_api_resp_path, "r") as file:
            swagger_api_resp = json.loads(file.read())

        with patch(
            "pymock_api.model.api_config.MockAPIs.template", new_callable=PropertyMock
        ) as mock_mock_apis_template:
            template_config = TemplateConfig()
            # Set the base file path to let the test could run and save the result configuration under the target
            # directory
            template_config.values.base_file_path = str(test_scenario_dir)
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
                expected_config_data_modal = load_config(expected_yaml_config_path)

                # Verify
                mock_swagger_request.assert_called_once()
                ut_config_data_modal = load_config(ut_config_path)
                assert ut_config_data_modal
                assert expected_config_data_modal
                assert ut_config_data_modal.name == expected_config_data_modal.name
                assert ut_config_data_modal.description == expected_config_data_modal.description
                assert ut_config_data_modal.apis
                assert expected_config_data_modal.apis
                assert ut_config_data_modal.apis == expected_config_data_modal.apis
