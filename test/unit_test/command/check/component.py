import json
from typing import Union
from unittest.mock import MagicMock, Mock, patch

import pytest

from pymock_server.command.check.component import (
    SubCmdCheckComponent,
    SwaggerDiffChecking,
    ValidityChecking,
)
from pymock_server.command.options import SubCommand, SysArg
from pymock_server.model import (
    ParserArguments,
    SubcmdAddArguments,
    SubcmdCheckArguments,
    SubcmdGetArguments,
    SubcmdRunArguments,
    deserialize_api_doc_config,
    load_config,
)

from ...._values import (
    _Bind_Host_And_Port,
    _Generate_Sample,
    _Log_Level,
    _Print_Sample,
    _Sample_File_Path,
    _Swagger_API_Document_URL,
    _Test_Config,
    _Test_SubCommand_Check,
    _Workers_Amount,
)
from ._test_case import (
    SubCmdCheckComponentTestCaseFactory,
    SwaggerDiffCheckTestCaseFactory,
)


def _given_parser_args(
    subcommand: str = None,
    app_type: str = None,
    config_path: str = None,
    swagger_doc_url: str = None,
    stop_if_fail: bool = True,
) -> Union[SubcmdRunArguments, SubcmdAddArguments, SubcmdCheckArguments, SubcmdGetArguments, ParserArguments]:
    if subcommand == "run":
        return SubcmdRunArguments(
            subparser_name=subcommand,
            app_type=app_type,
            config=_Test_Config,
            bind=_Bind_Host_And_Port.value,
            workers=_Workers_Amount.value,
            log_level=_Log_Level.value,
        )
    elif subcommand == "config":
        return SubcmdAddArguments(
            subparser_name=subcommand,
            print_sample=_Print_Sample,
            generate_sample=_Generate_Sample,
            sample_output_path=_Sample_File_Path,
        )
    elif subcommand == "check":
        return SubcmdCheckArguments(
            subparser_name=subcommand,
            subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Check]),
            config_path=(config_path or _Test_Config),
            swagger_doc_url=swagger_doc_url,
            stop_if_fail=stop_if_fail,
            check_api_path=True,
            check_api_parameters=True,
            check_api_http_method=True,
        )
    elif subcommand == "inspect":
        return SubcmdGetArguments(
            subparser_name=subcommand,
            config_path=(config_path or _Test_Config),
        )
    else:
        return ParserArguments(
            subparser_name=None,
        )


SubCmdCheckComponentTestCaseFactory.load(has_base_info=False, config_type="valid", exit_code=0)
SubCmdCheckComponentTestCaseFactory.load(has_base_info=True, config_type="valid", exit_code=0)
SubCmdCheckComponentTestCaseFactory.load(has_base_info=False, config_type="invalid", exit_code=1)
SUBCMD_CHECK_COMPONENT_TEST_CASE = SubCmdCheckComponentTestCaseFactory.get_test_case()

SwaggerDiffCheckTestCaseFactory.load()
SWAGGER_DIFF_CHECKER_TEST_CASE = SwaggerDiffCheckTestCaseFactory.get_test_case()


class TestSubCmdCheckComponent:
    @pytest.fixture(scope="class")
    def subcmd(self) -> SubCmdCheckComponent:
        return SubCmdCheckComponent()

    @pytest.mark.parametrize(
        ("api_resp_path", "dummy_yaml_path", "stop_if_fail", "expected_exit_code"),
        SUBCMD_CHECK_COMPONENT_TEST_CASE,
    )
    def test_with_command_processor_of_diff_swagger(
        self,
        api_resp_path: str,
        dummy_yaml_path: str,
        stop_if_fail: bool,
        expected_exit_code: str,
        subcmd: SubCmdCheckComponent,
    ):
        kwargs = {
            "api_resp_path": api_resp_path,
            "dummy_yaml_path": dummy_yaml_path,
            "stop_if_fail": stop_if_fail,
            "expected_exit_code": expected_exit_code,
            "subcmd": subcmd,
        }
        self._test_process_of_diff_swagger(**kwargs)

    def _test_process_of_diff_swagger(
        self,
        api_resp_path: str,
        dummy_yaml_path: str,
        expected_exit_code: str,
        subcmd: SubCmdCheckComponent,
        stop_if_fail: bool,
    ):
        mock_parser_arg = _given_parser_args(
            subcommand=_Test_SubCommand_Check, swagger_doc_url=_Swagger_API_Document_URL, stop_if_fail=stop_if_fail
        )
        with patch("pymock_server.command.check.component.load_config") as mock_load_config:
            mock_load_config.return_value = load_config(dummy_yaml_path)
            with patch.object(SwaggerDiffChecking, "_get_swagger_config") as mock_get_swagger_config:
                with open(api_resp_path, "r", encoding="utf-8") as file_stream:
                    mock_get_swagger_config.return_value = deserialize_api_doc_config(json.loads(file_stream.read()))

                with pytest.raises(SystemExit) as exc_info:
                    subcmd.process(parser=Mock(), args=mock_parser_arg)
                assert expected_exit_code in str(exc_info.value)

    @pytest.mark.parametrize(
        ("mock_exception", "stop_if_fail"),
        [
            (RuntimeError, True),
            (ValueError("not match invalid strategy error message"), True),
            (RuntimeError, False),
            (ValueError("not match invalid strategy error message"), False),
        ],
    )
    def test_process_raise_unexpected_exception(
        self, mock_exception: Exception, stop_if_fail: bool, subcmd: SubCmdCheckComponent
    ):
        mock_parser_arg = _given_parser_args(
            subcommand=_Test_SubCommand_Check, swagger_doc_url=_Swagger_API_Document_URL, stop_if_fail=stop_if_fail
        )
        MagicMock()
        with patch("pymock_server.command.check.component.load_config", side_effect=mock_exception) as mock_load_config:
            with pytest.raises(Exception):
                subcmd.process(parser=Mock(), args=mock_parser_arg)
            mock_load_config.assert_called_once()


class TestValidityChecking:
    @pytest.fixture(scope="class")
    def checking(self) -> ValidityChecking:
        return ValidityChecking()


class TestSwaggerDiffChecking:
    @pytest.fixture(scope="class")
    def checking(self) -> SwaggerDiffChecking:
        return SwaggerDiffChecking()

    @pytest.mark.parametrize("swagger_config_response", SWAGGER_DIFF_CHECKER_TEST_CASE)
    def test__get_swagger_config(self, swagger_config_response: str, checking: SwaggerDiffChecking):
        with patch("pymock_server.command.check.component.URLLibHTTPClient.request") as mock_api_client_request:
            with open(swagger_config_response, "r", encoding="utf-8") as file_stream:
                mock_api_client_request.return_value = json.loads(file_stream.read())

            checking._get_swagger_config(_Swagger_API_Document_URL)
            mock_api_client_request.assert_called_once_with(method="GET", url=_Swagger_API_Document_URL)
