import json
import pathlib
from test._values import _API_Doc_Source, _API_Doc_Source_File, _Test_Request_With_Https
from unittest.mock import Mock, PropertyMock, patch

import pytest

from pymock_server.command.options import SubCommand
from pymock_server.command.rest_server.pull.component import SubCmdPullComponent
from pymock_server.model import (
    SubcmdPullArguments,
    deserialize_api_doc_config,
    load_config,
)
from pymock_server.model.api_config import DivideStrategy, TemplateConfig
from pymock_server.model.rest_api_doc_config.base_config import set_component_definition
from pymock_server.model.subcmd_common import SysArg

from ._test_case import (
    PullOpenAPIDocConfigAsDividingConfigTestCaseFactory,
    SubCmdPullTestArgs,
)

PullOpenAPIDocConfigAsDividingConfigTestCaseFactory.load()
PULL_OPENAPI_DOC_AS_DIVIDING_CONFIG_TEST_CASE = PullOpenAPIDocConfigAsDividingConfigTestCaseFactory.get_test_case()


_OpenAPI_Doc_Config: dict = {
    "openapi": "3.0.2",
    "info": {"title": "FastAPI", "version": "0.1.0"},
    "paths": {
        "/foo": {
            "get": {
                "summary": "Foo Home",
                "operationId": "foo_home_foo_get",
                "parameters": [
                    {
                        "required": False,
                        "schema": {"title": "Arg1", "type": "string", "default": "arg1_default_value"},
                        "name": "arg1",
                        "in": "query",
                    },
                    {
                        "required": False,
                        "schema": {"title": "Arg2", "type": "integer", "default": 0},
                        "name": "arg2",
                        "in": "query",
                    },
                    {
                        "required": False,
                        "schema": {"title": "Arg3", "type": "boolean", "default": False},
                        "name": "arg3",
                        "in": "query",
                    },
                ],
                "responses": {
                    "200": {"description": "Successful Response", "content": {"application/json": {"schema": {}}}},
                    "422": {
                        "description": "Validation Error",
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/HTTPValidationError"}}
                        },
                    },
                },
            }
        }
    },
    "components": {
        "schemas": {
            "HTTPValidationError": {
                "title": "HTTPValidationError",
                "type": "object",
                "properties": {
                    "detail": {
                        "title": "Detail",
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/ValidationError"},
                    }
                },
            },
            "ValidationError": {
                "title": "ValidationError",
                "required": ["loc", "msg", "type"],
                "type": "object",
                "properties": {
                    "loc": {
                        "title": "Location",
                        "type": "array",
                        "items": {"anyOf": [{"type": "string"}, {"type": "integer"}]},
                    },
                    "msg": {"title": "Message", "type": "string"},
                    "type": {"title": "Error Type", "type": "string"},
                },
            },
        }
    },
}


class TestSubCmdPullComponent:
    @pytest.fixture(scope="function")
    def sub_cmd(self) -> SubCmdPullComponent:
        return SubCmdPullComponent()

    @pytest.mark.parametrize(
        "cmd_args",
        [
            # Not dry run
            # Doesn't include template section config
            SubcmdPullArguments(
                subparser_name=SubCommand.Pull,
                subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Pull]),
                request_with_https=_Test_Request_With_Https,
                source=_API_Doc_Source,
                source_file=_API_Doc_Source_File,
                config_path="./api.yaml",
                base_url="",
                include_template_config=False,
                base_file_path="/",
                dry_run=False,
                divide_api=False,
                divide_http=False,
                divide_http_request=False,
                divide_http_response=False,
            ),
            SubcmdPullArguments(
                subparser_name=SubCommand.Pull,
                subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Pull]),
                request_with_https=_Test_Request_With_Https,
                source=_API_Doc_Source,
                source_file=_API_Doc_Source_File,
                config_path="./test_dir/api.yaml",
                base_url="",
                include_template_config=False,
                base_file_path="./test_dir",
                dry_run=False,
                divide_api=False,
                divide_http=False,
                divide_http_request=False,
                divide_http_response=False,
            ),
            # Not dry run
            # Include template section config
            SubcmdPullArguments(
                subparser_name=SubCommand.Pull,
                subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Pull]),
                request_with_https=_Test_Request_With_Https,
                source=_API_Doc_Source,
                source_file=_API_Doc_Source_File,
                config_path="./api.yaml",
                base_url="",
                include_template_config=True,
                base_file_path="/",
                dry_run=False,
                divide_api=False,
                divide_http=False,
                divide_http_request=False,
                divide_http_response=False,
            ),
            SubcmdPullArguments(
                subparser_name=SubCommand.Pull,
                subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Pull]),
                request_with_https=_Test_Request_With_Https,
                source=_API_Doc_Source,
                source_file=_API_Doc_Source_File,
                config_path="./test_dir/api.yaml",
                base_url="",
                include_template_config=True,
                base_file_path="./test_dir",
                dry_run=False,
                divide_api=False,
                divide_http=False,
                divide_http_request=False,
                divide_http_response=False,
            ),
            # Dry run
            # Doesn't include template section config
            SubcmdPullArguments(
                subparser_name=SubCommand.Pull,
                subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Pull]),
                request_with_https=_Test_Request_With_Https,
                source=_API_Doc_Source,
                source_file=_API_Doc_Source_File,
                config_path="./api.yaml",
                base_url="",
                include_template_config=False,
                base_file_path="/",
                dry_run=True,
                divide_api=False,
                divide_http=False,
                divide_http_request=False,
                divide_http_response=False,
            ),
            SubcmdPullArguments(
                subparser_name=SubCommand.Pull,
                subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Pull]),
                request_with_https=_Test_Request_With_Https,
                source=_API_Doc_Source,
                source_file=_API_Doc_Source_File,
                config_path="./test_dir/api.yaml",
                base_url="",
                include_template_config=False,
                base_file_path="./test_dir",
                dry_run=True,
                divide_api=False,
                divide_http=False,
                divide_http_request=False,
                divide_http_response=False,
            ),
            # Dry run
            # Include template section config
            SubcmdPullArguments(
                subparser_name=SubCommand.Pull,
                subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Pull]),
                request_with_https=_Test_Request_With_Https,
                source=_API_Doc_Source,
                source_file=_API_Doc_Source_File,
                config_path="./api.yaml",
                base_url="",
                include_template_config=True,
                base_file_path="/",
                dry_run=True,
                divide_api=True,
                divide_http=False,
                divide_http_request=False,
                divide_http_response=False,
            ),
            SubcmdPullArguments(
                subparser_name=SubCommand.Pull,
                subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Pull]),
                request_with_https=_Test_Request_With_Https,
                source=_API_Doc_Source,
                source_file=_API_Doc_Source_File,
                config_path="./test_dir/api.yaml",
                base_url="",
                include_template_config=True,
                base_file_path="./test_dir",
                dry_run=True,
                divide_api=True,
                divide_http=False,
                divide_http_request=False,
                divide_http_response=False,
            ),
        ],
    )
    def test_command_line_argument_setting(self, sub_cmd: SubCmdPullComponent, cmd_args: SubcmdPullArguments):
        # Mock function and its return value if it needs
        with patch.object(sub_cmd, "_get_openapi_doc_config") as mock_get_openapi_doc_config:
            openapi_doc_config = deserialize_api_doc_config(data=_OpenAPI_Doc_Config)
            mock_get_openapi_doc_config.return_value = openapi_doc_config
            with patch(
                "pymock_server.command._common.component.SavingConfigComponent._dry_run_final_process"
            ) as mock_dry_run_final_process:
                with patch(
                    "pymock_server.command._common.component.SavingConfigComponent._final_process"
                ) as mock_final_process:
                    # Run target function
                    sub_cmd.process(parser=Mock(), args=cmd_args)

                    # Verify
                    http_proto = "https" if cmd_args.request_with_https else "http"
                    openapi_doc_url = f"{http_proto}://{cmd_args.source}"
                    mock_get_openapi_doc_config.assert_called_once_with(
                        url=openapi_doc_url, config_file=cmd_args.source_file
                    )

                    api_config = openapi_doc_config.to_api_config(base_url=cmd_args.base_url)
                    # Some settings
                    api_config.is_pull = True
                    api_config.dry_run = cmd_args.dry_run
                    api_config.divide_strategy = DivideStrategy(
                        divide_api=cmd_args.divide_api,
                        divide_http=cmd_args.divide_http,
                        divide_http_request=cmd_args.divide_http_request,
                        divide_http_response=cmd_args.divide_http_response,
                    )
                    api_config.set_template_in_config = cmd_args.include_template_config
                    # The property *base_file_path* in template section part
                    assert api_config.apis
                    assert api_config.apis.template
                    api_config.apis.template.file.config_path_values.base_file_path = cmd_args.base_file_path
                    api_config_serialize_data = api_config.serialize()
                    if cmd_args.dry_run:
                        mock_dry_run_final_process.assert_called_once_with(cmd_args, api_config_serialize_data)
                        mock_final_process.assert_not_called()
                    else:
                        mock_dry_run_final_process.assert_not_called()
                        mock_final_process.assert_called_once_with(cmd_args, api_config_serialize_data)

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
        test_scenario_dir = pathlib.Path(swagger_api_resp_path).parent
        under_test_dir = "v3_openapi" if "v3" in swagger_api_resp_path else "v2_openapi"
        ut_dir = pathlib.Path(test_scenario_dir, "under_test", under_test_dir)
        if not ut_dir.exists():
            ut_dir.mkdir(parents=True)
        ut_config_path = str(pathlib.Path(ut_dir, "api.yaml"))
        cmd_args = SubcmdPullArguments(
            subparser_name=SubCommand.Pull,
            subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Pull]),
            request_with_https=_Test_Request_With_Https,
            source=_API_Doc_Source,
            source_file=_API_Doc_Source_File,
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
            "pymock_server.model.api_config.MockAPIs.template", new_callable=PropertyMock
        ) as mock_mock_apis_template:
            template_config = TemplateConfig()
            template_config.file.config_path_values.base_file_path = str(ut_dir)
            mock_mock_apis_template.return_value = template_config

            # Set the Swagger API reference data for testing
            openapi_schema_key = "components" if "v3" in swagger_api_resp_path else "definitions"
            set_component_definition(swagger_api_resp.get(openapi_schema_key, {}))
            # Mock the HTTP request result as the Swagger API documentation data
            with patch(
                "pymock_server.command.rest_server.pull.component.URLLibHTTPClient.request",
                return_value=swagger_api_resp,
            ) as mock_swagger_request:
                # Run target function
                sub_cmd.process(parser=Mock(), args=cmd_args)

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
