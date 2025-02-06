import sys
from argparse import Namespace
from typing import Callable, List, Optional, Type
from unittest.mock import MagicMock, Mock, patch

import pytest

# isort: off

from test._values import (
    SubCommand,
    _Test_Config,
    _Test_HTTP_Method,
    _Test_HTTP_Resp,
    _Test_Response_Strategy,
    _Test_URL,
)
from test.unit_test.command._base.process import BaseCommandProcessorTestSpec

# isort: on

from fake_api_server.command._common.component import SavingConfigComponent
from fake_api_server.command.rest_server.add.process import SubCmdAdd
from fake_api_server.command.subcommand import SubCommandLine
from fake_api_server.model import SubcmdAddArguments
from fake_api_server.model.api_config.apis import ResponseStrategy
from fake_api_server.model.subcmd_common import SysArg


class FakeSavingConfigComponent(SavingConfigComponent):
    pass


class TestSubCmdAdd(BaseCommandProcessorTestSpec):
    @pytest.fixture(scope="function")
    def cmd_ps(self) -> SubCmdAdd:
        return SubCmdAdd()

    @pytest.mark.parametrize(
        ("url_path", "method", "params", "response_strategy", "response_value"),
        [
            ("/foo", "", [], _Test_Response_Strategy, [""]),
            ("/foo", "GET", [], _Test_Response_Strategy, [""]),
            ("/foo", "POST", [], _Test_Response_Strategy, ["This is PyTest response"]),
            ("/foo", "PUT", [], _Test_Response_Strategy, ["Wow testing."]),
            ("/foo-file", "PUT", [], ResponseStrategy.FILE, [_Test_Config]),
            (
                "/foo-object",
                "PUT",
                [],
                ResponseStrategy.OBJECT,
                [{"name": "arg", "required": True, "type": "str", "format": None}],
            ),
            ("/foo-object", "PUT", [], ResponseStrategy.OBJECT, []),
        ],
    )
    def test_with_command_processor(
        self,
        url_path: str,
        method: str,
        params: List[dict],
        response_strategy: ResponseStrategy,
        response_value: List[str],
        object_under_test: Callable,
    ):
        kwargs = {
            "url_path": url_path,
            "method": method,
            "params": params,
            "response_strategy": response_strategy,
            "response_value": response_value,
            "cmd_ps": object_under_test,
        }
        self._test_process(**kwargs)

    @pytest.mark.parametrize(
        ("url_path", "method", "params", "response_strategy", "response_value"),
        [
            ("/foo", "", "", _Test_Response_Strategy, [""]),
            ("/foo", "GET", [], _Test_Response_Strategy, [""]),
            ("/foo", "POST", [], _Test_Response_Strategy, ["This is PyTest response"]),
            ("/foo", "PUT", [], _Test_Response_Strategy, ["Wow testing."]),
            ("/foo-file", "PUT", [], ResponseStrategy.FILE, [_Test_Config]),
            (
                "/foo-object",
                "PUT",
                [],
                ResponseStrategy.OBJECT,
                [{"name": "arg", "required": True, "type": "str", "format": None}],
            ),
            ("/foo-object", "PUT", [], ResponseStrategy.OBJECT, []),
        ],
    )
    def test_with_run_entry_point(
        self,
        url_path: str,
        method: str,
        params: List[dict],
        response_strategy: ResponseStrategy,
        response_value: List[str],
        entry_point_under_test: Callable,
    ):
        kwargs = {
            "url_path": url_path,
            "method": method,
            "params": params,
            "response_strategy": response_strategy,
            "response_value": response_value,
            "cmd_ps": entry_point_under_test,
        }
        self._test_process(**kwargs)

    def _test_process(
        self,
        url_path: str,
        method: str,
        params: List[dict],
        response_strategy: ResponseStrategy,
        response_value: List[str],
        cmd_ps: Callable,
    ):
        FakeSavingConfigComponent.serialize_and_save = MagicMock()
        mock_parser_arg = SubcmdAddArguments(
            subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Add]),
            config_path=_Test_Config,
            tag="",
            api_path=url_path,
            http_method=method,
            parameters=params,
            response_strategy=response_strategy,
            response_value=response_value,
            include_template_config=False,
            base_file_path="./",
            base_url="",
            dry_run=False,
            divide_api=False,
            divide_http=False,
            divide_http_request=False,
            divide_http_response=False,
        )
        cmd_parser = Mock()

        with patch.object(sys, "argv", self._given_command_line()):
            with patch(
                "fake_api_server.command.rest_server.add.component.SavingConfigComponent",
                return_value=FakeSavingConfigComponent,
            ) as mock_saving_config_component:
                cmd_ps(cmd_parser, mock_parser_arg)

                mock_saving_config_component.assert_called_once()
                FakeSavingConfigComponent.serialize_and_save.assert_called_once()

    def _given_command_line(self) -> List[str]:
        return ["rest-server", "add"]

    def _given_cmd_args_namespace(self) -> Namespace:
        args_namespace = Namespace()
        args_namespace.subcommand = SubCommand.RestServer
        setattr(args_namespace, SubCommand.RestServer, SubCommand.Add)
        args_namespace.config_path = ""
        args_namespace.tag = ""
        args_namespace.api_path = _Test_URL
        args_namespace.http_method = _Test_HTTP_Method
        args_namespace.parameters = ""
        args_namespace.response_strategy = _Test_Response_Strategy
        args_namespace.response_value = _Test_HTTP_Resp
        args_namespace.include_template_config = False
        args_namespace.base_file_path = "./"
        args_namespace.base_url = ""
        args_namespace.dry_run = False
        args_namespace.divide_api = False
        args_namespace.divide_http = False
        args_namespace.divide_http_request = False
        args_namespace.divide_http_response = False
        return args_namespace

    def _given_subcmd(self) -> Optional[SysArg]:
        return SysArg(
            pre_subcmd=SysArg(pre_subcmd=SysArg(subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer),
            subcmd=SubCommandLine.Add,
        )

    def _expected_argument_type(self) -> Type[SubcmdAddArguments]:
        return SubcmdAddArguments
