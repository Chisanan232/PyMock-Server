from unittest.mock import patch

import pytest

from pymock_api.command._common.component import SavingConfigComponent
from pymock_api.command.add.component import SubCmdAddComponent
from pymock_api.command.options import SubCommand
from pymock_api.model import SubcmdAddArguments, deserialize_openapi_doc_config
from pymock_api.model.enums import ResponseStrategy

from ...._values import (
    _Dummy_Add_Arg_Parameter,
    _generate_response_for_add,
    _Test_HTTP_Method,
    _Test_URL,
)

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
                config_path="./api.yaml",
                # new mock API
                api_path=_Test_URL,
                http_method=_Test_HTTP_Method,
                parameters=_Dummy_Add_Arg_Parameter,
                response_strategy=_Dummy_Add_Arg_Strategy,
                response_value=_Dummy_Add_Arg_Values,
                # saving details
                include_template_config=False,
                base_file_path="./",
                dry_run=False,
                divide_api=False,
                divide_http=False,
                divide_http_request=False,
                divide_http_response=False,
            ),
            SubcmdAddArguments(
                subparser_name=SubCommand.Add,
                config_path="./test_dir/api.yaml",
                # new mock API
                api_path=_Test_URL,
                http_method=_Test_HTTP_Method,
                parameters=_Dummy_Add_Arg_Parameter,
                response_strategy=_Dummy_Add_Arg_Strategy,
                response_value=_Dummy_Add_Arg_Values,
                # saving details
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
            SubcmdAddArguments(
                subparser_name=SubCommand.Add,
                config_path="./api.yaml",
                # new mock API
                api_path=_Test_URL,
                http_method=_Test_HTTP_Method,
                parameters=_Dummy_Add_Arg_Parameter,
                response_strategy=_Dummy_Add_Arg_Strategy,
                response_value=_Dummy_Add_Arg_Values,
                # saving details
                include_template_config=True,
                base_file_path="./",
                dry_run=False,
                divide_api=False,
                divide_http=False,
                divide_http_request=False,
                divide_http_response=False,
            ),
            SubcmdAddArguments(
                subparser_name=SubCommand.Add,
                config_path="./test_dir/api.yaml",
                # new mock API
                api_path=_Test_URL,
                http_method=_Test_HTTP_Method,
                parameters=_Dummy_Add_Arg_Parameter,
                response_strategy=_Dummy_Add_Arg_Strategy,
                response_value=_Dummy_Add_Arg_Values,
                # saving details
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
            SubcmdAddArguments(
                subparser_name=SubCommand.Add,
                config_path="./api.yaml",
                # new mock API
                api_path=_Test_URL,
                http_method=_Test_HTTP_Method,
                parameters=_Dummy_Add_Arg_Parameter,
                response_strategy=_Dummy_Add_Arg_Strategy,
                response_value=_Dummy_Add_Arg_Values,
                # saving details
                include_template_config=False,
                base_file_path="./",
                dry_run=True,
                divide_api=False,
                divide_http=False,
                divide_http_request=False,
                divide_http_response=False,
            ),
            SubcmdAddArguments(
                subparser_name=SubCommand.Add,
                config_path="./test_dir/api.yaml",
                # new mock API
                api_path=_Test_URL,
                http_method=_Test_HTTP_Method,
                parameters=_Dummy_Add_Arg_Parameter,
                response_strategy=_Dummy_Add_Arg_Strategy,
                response_value=_Dummy_Add_Arg_Values,
                # saving details
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
            SubcmdAddArguments(
                subparser_name=SubCommand.Add,
                config_path="./api.yaml",
                # new mock API
                api_path=_Test_URL,
                http_method=_Test_HTTP_Method,
                parameters=_Dummy_Add_Arg_Parameter,
                response_strategy=_Dummy_Add_Arg_Strategy,
                response_value=_Dummy_Add_Arg_Values,
                # saving details
                include_template_config=True,
                base_file_path="./",
                dry_run=True,
                divide_api=True,
                divide_http=False,
                divide_http_request=False,
                divide_http_response=False,
            ),
            SubcmdAddArguments(
                subparser_name=SubCommand.Add,
                config_path="./test_dir/api.yaml",
                # new mock API
                api_path=_Test_URL,
                http_method=_Test_HTTP_Method,
                parameters=_Dummy_Add_Arg_Parameter,
                response_strategy=_Dummy_Add_Arg_Strategy,
                response_value=_Dummy_Add_Arg_Values,
                # saving details
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
    def test_command_line_argument_setting(self, sub_cmd: SubCmdAddComponent, cmd_args: SubcmdAddArguments):
        # Mock function and its return value if it needs
        with patch.object(sub_cmd, "_get_api_config") as mock_get_api_config:
            openapi_doc_config = deserialize_openapi_doc_config(data=_OpenAPI_Doc_Config)
            api_config = openapi_doc_config.to_api_config(base_url="")
            mock_get_api_config.return_value = api_config
            with patch(
                "pymock_api.command._common.component.SavingConfigComponent._dry_run_final_process"
            ) as mock_dry_run_final_process:
                with patch(
                    "pymock_api.command._common.component.SavingConfigComponent._final_process"
                ) as mock_final_process:
                    # Run target function
                    sub_cmd.process(args=cmd_args)

                    # Verify
                    new_api_config = sub_cmd._generate_api_config(api_config=api_config, args=cmd_args)
                    api_config_serialize_data = SavingConfigComponent().serialize_api_config_with_cmd_args(
                        cmd_args=cmd_args, api_config=new_api_config
                    )
                    if cmd_args.dry_run:
                        mock_dry_run_final_process.assert_called_once_with(api_config_serialize_data)
                        mock_final_process.assert_not_called()
                    else:
                        mock_dry_run_final_process.assert_not_called()
                        mock_final_process.assert_called_once_with(cmd_args, api_config_serialize_data)
