import json
import pathlib
from unittest.mock import PropertyMock, patch

import pytest

from pymock_api.command.options import SubCommand
from pymock_api.command.pull.component import SubCmdPullComponent
from pymock_api.model import SubcmdPullArguments, load_config
from pymock_api.model.api_config import TemplateConfig
from pymock_api.model.openapi._schema_parser import (
    OpenAPIV2SchemaParser,
    set_component_definition,
)

from ...._values import _API_Doc_Source, _Test_Request_With_Https
from ._test_case import (
    PullOpenAPIDocConfigAsDividingConfigTestCaseFactory,
    SubCmdPullTestArgs,
)

PullOpenAPIDocConfigAsDividingConfigTestCaseFactory.load()
PULL_OPENAPI_DOC_AS_DIVIDING_CONFIG_TEST_CASE = PullOpenAPIDocConfigAsDividingConfigTestCaseFactory.get_test_case()


class TestSubCmdPullComponent:
    @pytest.fixture(scope="function")
    def sub_cmd(self) -> SubCmdPullComponent:
        return SubCmdPullComponent()

    @pytest.mark.parametrize(
        ("swagger_api_resp_path", "cmd_arg", "expected_yaml_config_path"), PULL_OPENAPI_DOC_AS_DIVIDING_CONFIG_TEST_CASE
    )
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

        # Note: Set the base file path to let the test could run and save the result configuration under the target
        # directory
        with patch(
            "pymock_api.model.api_config.MockAPIs.template", new_callable=PropertyMock
        ) as mock_mock_apis_template:
            template_config = TemplateConfig()
            template_config.values.base_file_path = str(ut_dir)
            mock_mock_apis_template.return_value = template_config

            # Set the Swagger API reference data for testing
            set_component_definition(OpenAPIV2SchemaParser(data=swagger_api_resp))
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
                for api_key in ut_config_data_modal.apis.apis.keys():
                    ut_api = ut_config_data_modal.apis.apis[api_key]
                    expect_api = expected_config_data_modal.apis.apis[api_key]

                    # Basic checking
                    assert ut_api is not None
                    assert expect_api is not None
                    assert ut_api.http is not None
                    assert expect_api.http is not None
                    assert ut_api.http.request is not None
                    assert ut_api.http.response is not None
                    assert expect_api.http.request is not None
                    assert expect_api.http.response is not None

                    # Details checking
                    assert ut_api.url == expect_api.url
                    assert ut_api.tag == expect_api.tag
                    assert ut_api.http.request.method == expect_api.http.request.method
                    assert ut_api.http.request.parameters == expect_api.http.request.parameters
                    assert ut_api.http.response.strategy == expect_api.http.response.strategy
                    assert ut_api.http.response.value == expect_api.http.response.value
                    assert ut_api.http.response.path == expect_api.http.response.path
                    assert ut_api.http.response.properties == expect_api.http.response.properties
