import sys
from argparse import Namespace
from typing import Callable, List, Optional, Type
from unittest.mock import MagicMock, Mock, patch

import pytest

# isort: off
from test._values import (
    SubCommand,
    _Bind_Host_And_Port,
    _Log_Level,
    _Test_App_Type,
    _Test_Auto_Type,
    _Test_Config,
    _Test_FastAPI_App_Type,
    _Workers_Amount,
)
from test.unit_test.command._base.process import BaseCommandProcessorTestSpec

# isort: on

from pymock_server.command.rest_server.run.process import SubCmdRun
from pymock_server.command.subcommand import SubCommandLine
from pymock_server.model import SubcmdRunArguments
from pymock_server.model.subcmd_common import SysArg
from pymock_server.server import ASGIServer, Command, CommandOptions, WSGIServer


class TestSubCmdRun(BaseCommandProcessorTestSpec):
    @pytest.fixture(scope="function")
    def cmd_ps(self) -> SubCmdRun:
        return SubCmdRun()

    @pytest.mark.parametrize(
        ("app_type", "should_raise_exc"),
        [
            (_Test_App_Type, False),
            (_Test_FastAPI_App_Type, False),
            (_Test_Auto_Type, False),
            ("invalid app-type which is not a Python web library or framework", True),
        ],
    )
    def test_with_command_processor(self, app_type: str, should_raise_exc: bool, object_under_test: Callable):
        kwargs = {
            "app_type": app_type,
            "should_raise_exc": should_raise_exc,
            "cmd_ps": object_under_test,
        }
        self._test_process(**kwargs)

    @pytest.mark.parametrize(
        ("app_type", "should_raise_exc"),
        [
            (_Test_App_Type, False),
            (_Test_FastAPI_App_Type, False),
            (_Test_Auto_Type, False),
            ("invalid app-type which is not a Python web library or framework", True),
        ],
    )
    def test_with_run_entry_point(self, app_type: str, should_raise_exc: bool, entry_point_under_test: Callable):
        kwargs = {
            "app_type": app_type,
            "should_raise_exc": should_raise_exc,
            "cmd_ps": entry_point_under_test,
        }
        self._test_process(**kwargs)

    def _test_process(self, app_type: str, should_raise_exc: bool, cmd_ps: Callable):
        mock_parser_arg = self._given_parser_args(app_type=app_type)
        command = self._given_command(app_type="Python web library")
        command.run = MagicMock()
        cmd_parser = Mock()

        with patch.object(sys, "argv", self._given_command_line()):
            with patch.object(ASGIServer, "generate", return_value=command) as mock_asgi_generate:
                with patch.object(WSGIServer, "generate", return_value=command) as mock_wsgi_generate:
                    if should_raise_exc:
                        with pytest.raises(ValueError) as exc_info:
                            cmd_ps(cmd_parser, mock_parser_arg)
                        assert "Invalid value" in str(exc_info.value)
                        mock_asgi_generate.assert_not_called()
                        mock_wsgi_generate.assert_not_called()
                        command.run.assert_not_called()
                    else:
                        cmd_ps(cmd_parser, mock_parser_arg)
                        if app_type == "auto":
                            mock_asgi_generate.assert_called_once_with(mock_parser_arg)
                            mock_wsgi_generate.assert_not_called()
                        elif app_type == "flask":
                            mock_asgi_generate.assert_not_called()
                            mock_wsgi_generate.assert_called_once_with(mock_parser_arg)
                        elif app_type == "fastapi":
                            mock_asgi_generate.assert_called_once_with(mock_parser_arg)
                            mock_wsgi_generate.assert_not_called()
                        else:
                            assert False, "Please use valid *app-type* option value."
                        command.run.assert_called_once()

    def _given_command_line(self) -> List[str]:
        return ["rest-server", "run"]

    def _given_parser_args(self, app_type: str) -> SubcmdRunArguments:
        return SubcmdRunArguments(
            subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Run]),
            app_type=app_type,
            config=_Test_Config,
            bind=_Bind_Host_And_Port.value,
            workers=_Workers_Amount.value,
            log_level=_Log_Level.value,
        )

    def _given_command(self, app_type: str) -> Command:
        mock_parser_arg = self._given_parser_args(app_type=app_type)
        mock_cmd_option_obj = self._given_command_option()
        return Command(entry_point="SGI tool command", app=mock_parser_arg.app_type, options=mock_cmd_option_obj)

    def _given_command_option(self) -> CommandOptions:
        return CommandOptions(bind=_Bind_Host_And_Port.value, workers=_Workers_Amount.value, log_level=_Log_Level.value)

    def _given_cmd_args_namespace(self) -> Namespace:
        args_namespace = Namespace()
        args_namespace.subcommand = SubCommand.RestServer
        setattr(args_namespace, SubCommand.RestServer, SubCommand.Run)
        args_namespace.config = _Test_Config
        args_namespace.app_type = _Test_App_Type
        args_namespace.bind = _Bind_Host_And_Port.value
        args_namespace.workers = _Workers_Amount.value
        args_namespace.log_level = _Log_Level.value
        return args_namespace

    def _given_subcmd(self) -> Optional[SysArg]:
        return SysArg(
            pre_subcmd=SysArg(pre_subcmd=SysArg(subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer),
            subcmd=SubCommandLine.Run,
        )

    def _expected_argument_type(self) -> Type[SubcmdRunArguments]:
        return SubcmdRunArguments
