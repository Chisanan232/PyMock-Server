import pathlib
from unittest.mock import Mock, PropertyMock, patch

import pytest

from pymock_server.command._common.component import SavingConfigComponent
from pymock_server.command.options import SubCommand, SysArg
from pymock_server.command.rest_server.add.component import SubCmdAddComponent
from pymock_server.model import (
    SubcmdAddArguments,
    TemplateConfig,
    deserialize_api_doc_config,
    load_config,
)
from pymock_server.model.api_config.apis import ResponseStrategy

from ...._values import (
    _Dummy_Add_Arg_Parameter,
    _generate_response_for_add,
    _Test_HTTP_Method,
    _Test_URL,
)
from ._test_case import AddMockAPIAsDividingConfigTestCaseFactory, SubCmdAddTestArgs

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
        },
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

_Dummy_Add_Arg_Strategy, _Dummy_Add_Arg_Values = _generate_response_for_add(ResponseStrategy.STRING)

AddMockAPIAsDividingConfigTestCaseFactory.load()
ADD_API_AS_DIVIDING_CONFIG_TEST_CASE = AddMockAPIAsDividingConfigTestCaseFactory.get_test_case()


class TestSubCmdAddComponent:
    @pytest.fixture(scope="function")
    def sub_cmd(self) -> SubCmdAddComponent:
        return SubCmdAddComponent()

    @pytest.mark.parametrize(
        "cmd_args",
        [
            # Not dry run
            # Doesn't include template section config
            SubcmdAddArguments(
                subparser_name=SubCommand.Add,
                subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Add]),
                config_path="./api.yaml",
                # new mock API
                tag="",
                api_path=_Test_URL,
                http_method=_Test_HTTP_Method,
                parameters=_Dummy_Add_Arg_Parameter,
                response_strategy=_Dummy_Add_Arg_Strategy,
                response_value=_Dummy_Add_Arg_Values,
                # saving details
                include_template_config=False,
                base_file_path="./",
                base_url="",
                divide_api=False,
                divide_http=False,
                divide_http_request=False,
                divide_http_response=False,
                dry_run=False,
            ),
            SubcmdAddArguments(
                subparser_name=SubCommand.Add,
                subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Add]),
                config_path="./test_dir/api.yaml",
                # new mock API
                tag="",
                api_path=_Test_URL,
                http_method=_Test_HTTP_Method,
                parameters=_Dummy_Add_Arg_Parameter,
                response_strategy=_Dummy_Add_Arg_Strategy,
                response_value=_Dummy_Add_Arg_Values,
                # saving details
                include_template_config=False,
                base_file_path="./test_dir",
                base_url="",
                divide_api=False,
                divide_http=False,
                divide_http_request=False,
                divide_http_response=False,
                dry_run=False,
            ),
            # Not dry run
            # Include template section config
            SubcmdAddArguments(
                subparser_name=SubCommand.Add,
                subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Add]),
                config_path="./api.yaml",
                # new mock API
                tag="",
                api_path=_Test_URL,
                http_method=_Test_HTTP_Method,
                parameters=_Dummy_Add_Arg_Parameter,
                response_strategy=_Dummy_Add_Arg_Strategy,
                response_value=_Dummy_Add_Arg_Values,
                # saving details
                include_template_config=True,
                base_file_path="./",
                base_url="",
                divide_api=False,
                divide_http=False,
                divide_http_request=False,
                divide_http_response=False,
                dry_run=False,
            ),
            SubcmdAddArguments(
                subparser_name=SubCommand.Add,
                subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Add]),
                config_path="./test_dir/api.yaml",
                # new mock API
                tag="",
                api_path=_Test_URL,
                http_method=_Test_HTTP_Method,
                parameters=_Dummy_Add_Arg_Parameter,
                response_strategy=_Dummy_Add_Arg_Strategy,
                response_value=_Dummy_Add_Arg_Values,
                # saving details
                include_template_config=True,
                base_file_path="./test_dir",
                base_url="",
                divide_api=False,
                divide_http=False,
                divide_http_request=False,
                divide_http_response=False,
                dry_run=False,
            ),
            # Dry run
            # Doesn't include template section config
            SubcmdAddArguments(
                subparser_name=SubCommand.Add,
                subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Add]),
                config_path="./api.yaml",
                # new mock API
                tag="",
                api_path=_Test_URL,
                http_method=_Test_HTTP_Method,
                parameters=_Dummy_Add_Arg_Parameter,
                response_strategy=_Dummy_Add_Arg_Strategy,
                response_value=_Dummy_Add_Arg_Values,
                # saving details
                include_template_config=False,
                base_file_path="./",
                base_url="",
                divide_api=False,
                divide_http=False,
                divide_http_request=False,
                divide_http_response=False,
                dry_run=True,
            ),
            SubcmdAddArguments(
                subparser_name=SubCommand.Add,
                subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Add]),
                config_path="./test_dir/api.yaml",
                # new mock API
                tag="",
                api_path=_Test_URL,
                http_method=_Test_HTTP_Method,
                parameters=_Dummy_Add_Arg_Parameter,
                response_strategy=_Dummy_Add_Arg_Strategy,
                response_value=_Dummy_Add_Arg_Values,
                # saving details
                include_template_config=False,
                base_file_path="./test_dir",
                base_url="",
                divide_api=False,
                divide_http=False,
                divide_http_request=False,
                divide_http_response=False,
                dry_run=True,
            ),
            # Dry run
            # Include template section config
            SubcmdAddArguments(
                subparser_name=SubCommand.Add,
                subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Add]),
                config_path="./api.yaml",
                # new mock API
                tag="",
                api_path=_Test_URL,
                http_method=_Test_HTTP_Method,
                parameters=_Dummy_Add_Arg_Parameter,
                response_strategy=_Dummy_Add_Arg_Strategy,
                response_value=_Dummy_Add_Arg_Values,
                # saving details
                include_template_config=True,
                base_file_path="./",
                base_url="",
                divide_api=True,
                divide_http=False,
                divide_http_request=False,
                divide_http_response=False,
                dry_run=True,
            ),
            SubcmdAddArguments(
                subparser_name=SubCommand.Add,
                subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Add]),
                config_path="./test_dir/api.yaml",
                # new mock API
                tag="",
                api_path=_Test_URL,
                http_method=_Test_HTTP_Method,
                parameters=_Dummy_Add_Arg_Parameter,
                response_strategy=_Dummy_Add_Arg_Strategy,
                response_value=_Dummy_Add_Arg_Values,
                # saving details
                include_template_config=True,
                base_file_path="./test_dir",
                base_url="",
                divide_api=True,
                divide_http=False,
                divide_http_request=False,
                divide_http_response=False,
                dry_run=True,
            ),
        ],
    )
    def test_command_line_argument_setting(self, sub_cmd: SubCmdAddComponent, cmd_args: SubcmdAddArguments):
        # Mock function and its return value if it needs
        with patch.object(sub_cmd, "_get_api_config") as mock_get_api_config:
            openapi_doc_config = deserialize_api_doc_config(data=_OpenAPI_Doc_Config)
            api_config = openapi_doc_config.to_api_config(base_url="")
            mock_get_api_config.return_value = api_config
            with patch(
                "pymock_server.command._common.component.SavingConfigComponent._dry_run_final_process"
            ) as mock_dry_run_final_process:
                with patch(
                    "pymock_server.command._common.component.SavingConfigComponent._final_process"
                ) as mock_final_process:
                    # Run target function
                    sub_cmd.process(parser=Mock(), args=cmd_args)

                    # Verify
                    new_api_config = sub_cmd._generate_api_config(api_config=api_config, args=cmd_args)
                    api_config_serialize_data = SavingConfigComponent().serialize_api_config_with_cmd_args(
                        cmd_args=cmd_args, api_config=new_api_config
                    )
                    if cmd_args.dry_run:
                        mock_dry_run_final_process.assert_called_once_with(cmd_args, api_config_serialize_data)
                        mock_final_process.assert_not_called()
                    else:
                        mock_dry_run_final_process.assert_not_called()
                        mock_final_process.assert_called_once_with(cmd_args, api_config_serialize_data)

    @pytest.mark.parametrize(
        ("under_test_api_config_dir", "cmd_arg", "expected_yaml_config_path"), ADD_API_AS_DIVIDING_CONFIG_TEST_CASE
    )
    def test_add_new_api_as_dividing_config(
        self,
        sub_cmd: SubCmdAddComponent,
        under_test_api_config_dir: str,
        cmd_arg: SubCmdAddTestArgs,
        expected_yaml_config_path: str,
    ):
        # Given command line argument
        under_test_dir = pathlib.Path(under_test_api_config_dir)
        # under_test_dir = "v3_openapi" if "v3" in under_test_api_config else "v2_openapi"
        # ut_dir = pathlib.Path(test_scenario_dir, "under_test", under_test_dir)
        if not under_test_dir.exists():
            under_test_dir.mkdir(parents=True)
        ut_config_path = str(pathlib.Path(under_test_dir, "api.yaml"))
        cmd_args = SubcmdAddArguments(
            subparser_name=SubCommand.Add,
            subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Add]),
            config_path=ut_config_path,
            # new mock API
            tag=cmd_arg.tag,
            api_path=_Test_URL,
            http_method=_Test_HTTP_Method,
            parameters=_Dummy_Add_Arg_Parameter,
            response_strategy=cmd_arg.resp_strategy,
            response_value=cmd_arg.resp_details,
            # saving details
            include_template_config=cmd_arg.include_template_config,
            base_file_path=str(under_test_dir),
            base_url=cmd_arg.base_url,
            divide_api=cmd_arg.divide_api,
            divide_http=cmd_arg.divide_http,
            divide_http_request=cmd_arg.divide_http_request,
            divide_http_response=cmd_arg.divide_http_response,
            dry_run=False,
        )

        # new_api_config_has_new_api = YAML().read(path=under_test_api_config)
        # with open(under_test_api_config, "r") as file:
        #     new_api_config_has_new_api = json.loads(file.read())

        # Note: Set the base file path to let the test could run and save the result configuration under the target
        # directory
        with patch(
            "pymock_server.model.api_config.MockAPIs.template", new_callable=PropertyMock
        ) as mock_mock_apis_template:
            template_config = TemplateConfig()
            template_config.file.config_path_values.base_file_path = str(under_test_dir)
            mock_mock_apis_template.return_value = template_config

            # Set the Swagger API reference data for testing
            # set_component_definition(OpenAPIV2SchemaParser(data=new_api_config_has_new_api))
            # Mock the HTTP request result as the Swagger API documentation data
            # with patch(
            #     "pymock_server.command.pull.component.URLLibHTTPClient.request", return_value=new_api_config_has_new_api
            # ) as mock_swagger_request:
            # Run target function
            sub_cmd.process(parser=Mock(), args=cmd_args)

            # Expected values
            expected_config_data_modal = load_config(expected_yaml_config_path, is_pull=True)

            # Verify
            # mock_swagger_request.assert_called_once()
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
