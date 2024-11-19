import json
from typing import Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

# isort: off

from test._values import (
    SubCommand,
    _Swagger_API_Document_URL,
    _Test_Config,
)

from ._test_case import (
    SubCmdCheckComponentTestCaseFactory,
    SwaggerDiffCheckTestCaseFactory,
)

# isort: on

from pymock_server.command.rest_server.check.component import (
    SubCmdCheckComponent,
    SwaggerDiffChecking,
    ValidityChecking,
)
from pymock_server.model import (
    SubcmdCheckArguments,
    deserialize_api_doc_config,
    load_config,
)
from pymock_server.model.subcmd_common import SysArg

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
        mock_parser_arg = self._given_parser_args(swagger_doc_url=_Swagger_API_Document_URL, stop_if_fail=stop_if_fail)
        with patch("pymock_server.command.rest_server.check.component.load_config") as mock_load_config:
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
        mock_parser_arg = self._given_parser_args(swagger_doc_url=_Swagger_API_Document_URL, stop_if_fail=stop_if_fail)
        MagicMock()
        with patch(
            "pymock_server.command.rest_server.check.component.load_config", side_effect=mock_exception
        ) as mock_load_config:
            with pytest.raises(Exception):
                subcmd.process(parser=Mock(), args=mock_parser_arg)
            mock_load_config.assert_called_once()

    def _given_parser_args(
        self, config_path: Optional[str] = None, swagger_doc_url: Optional[str] = None, stop_if_fail: bool = True
    ) -> SubcmdCheckArguments:
        return SubcmdCheckArguments(
            subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Check]),
            config_path=(config_path or _Test_Config),
            swagger_doc_url=swagger_doc_url,
            stop_if_fail=stop_if_fail,
            check_api_path=True,
            check_api_parameters=True,
            check_api_http_method=True,
        )


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
        with patch(
            "pymock_server.command.rest_server.check.component.URLLibHTTPClient.request"
        ) as mock_api_client_request:
            with open(swagger_config_response, "r", encoding="utf-8") as file_stream:
                mock_api_client_request.return_value = json.loads(file_stream.read())

            checking._get_swagger_config(_Swagger_API_Document_URL)
            mock_api_client_request.assert_called_once_with(method="GET", url=_Swagger_API_Document_URL)
