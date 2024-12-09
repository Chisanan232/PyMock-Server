import re
import sys
from argparse import ArgumentParser, Namespace
from enum import Enum
from typing import Callable, List, Optional, Type
from unittest.mock import MagicMock, Mock, patch

import pytest

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader  # type: ignore

from pymock_server.command._base.process import BaseCommandProcessor
from pymock_server.command.options import get_all_subcommands
from pymock_server.command.process import NoSubCmd, make_command_chain
from pymock_server.command.subcommand import SubCommandLine
from pymock_server.model import ParserArguments, SubcmdRunArguments
from pymock_server.model.subcmd_common import SysArg
from pymock_server.server import Command, CommandOptions, WSGIServer

# isort: off
from test._values import (
    SubCommand,
    _Bind_Host_And_Port,
    _Log_Level,
    _Test_Config,
    _Workers_Amount,
)
from test.unit_test.command._base.process import BaseCommandProcessorTestSpec

# isort: on


class FakeSubCommandLine(Enum):
    PyTest: str = "pytest-subcmd"
    Fake: str = "pytest-duplicated"


_Fake_SubCmd: FakeSubCommandLine = FakeSubCommandLine.PyTest
_Fake_SubCmd_Obj: SysArg = SysArg(subcmd=_Fake_SubCmd)
_Fake_Duplicated_SubCmd: FakeSubCommandLine = FakeSubCommandLine.Fake
_Fake_Duplicated_SubCmd_Obj: SysArg = SysArg(pre_subcmd=None, subcmd=_Fake_Duplicated_SubCmd)
_No_SubCmd_Amt: int = 1
_Fake_Amt: int = 1


def _given_command_option() -> CommandOptions:
    return CommandOptions(bind=_Bind_Host_And_Port.value, workers=_Workers_Amount.value, log_level=_Log_Level.value)


def _given_command(app_type: str) -> Command:
    mock_parser_arg = SubcmdRunArguments(
        subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Run]),
        app_type=app_type,
        config=_Test_Config,
        bind=_Bind_Host_And_Port.value,
        workers=_Workers_Amount.value,
        log_level=_Log_Level.value,
    )
    mock_cmd_option_obj = _given_command_option()
    return Command(entry_point="SGI tool command", app=mock_parser_arg.app_type, options=mock_cmd_option_obj)


class FakeCommandProcess(BaseCommandProcessor):
    responsible_subcommand: SysArg = _Fake_SubCmd_Obj

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> ParserArguments:
        return

    def _run(self, parser: ArgumentParser, args: ParserArguments) -> None:
        pass


class TestSubCmdProcessChain:
    @pytest.fixture(scope="class")
    def cmd_processor(self) -> FakeCommandProcess:
        return FakeCommandProcess()

    def test_next(self, cmd_processor: FakeCommandProcess):
        next_cmd = cmd_processor._next
        assert (next_cmd != cmd_processor) and (next_cmd is not cmd_processor)

    def test_next_exceed_length(self, cmd_processor: FakeCommandProcess):
        with pytest.raises(StopIteration):
            for _ in range(len(make_command_chain()) + 1):
                assert cmd_processor._next

    @pytest.mark.parametrize(
        ("subcmd", "expected_result"),
        [
            (_Fake_SubCmd_Obj, True),
            (_Fake_Duplicated_SubCmd_Obj, False),
        ],
    )
    def test_is_responsible(self, subcmd: SysArg, expected_result: bool, cmd_processor: FakeCommandProcess):
        is_responsible = cmd_processor._is_responsible(subcmd=subcmd)
        assert is_responsible is expected_result

    @pytest.mark.parametrize(
        ("chk_result", "should_dispatch"),
        [
            (True, False),
            (False, True),
        ],
    )
    def test_process(self, chk_result: bool, should_dispatch: bool, cmd_processor: FakeCommandProcess):
        cmd_processor._is_responsible = MagicMock(return_value=chk_result)
        cmd_processor._run = MagicMock()

        arg = ParserArguments(subparser_structure=_Fake_SubCmd_Obj)
        cmd_parser = Mock()
        cmd_processor.process(parser=cmd_parser, args=arg)

        cmd_processor._is_responsible.assert_called_once_with(subcmd=None)
        if should_dispatch:
            cmd_processor._run.assert_not_called()
        else:
            cmd_processor._run.assert_called_once_with(parser=cmd_parser, args=arg)

    @patch("copy.copy")
    def test_copy(self, mock_copy: Mock, cmd_processor: FakeCommandProcess):
        cmd_processor.copy()
        mock_copy.assert_called_once_with(cmd_processor)


class TestNoSubCmd(BaseCommandProcessorTestSpec):
    @pytest.fixture(scope="function")
    def cmd_ps(self) -> NoSubCmd:
        return NoSubCmd()

    def test_with_command_processor(self, object_under_test: Callable, **kwargs):
        with patch.object(sys, "argv", self._given_command_line()):
            kwargs = {
                "cmd_ps": object_under_test,
            }
            self._test_process(**kwargs)

    def test_with_run_entry_point(self, entry_point_under_test: Callable, **kwargs):
        with patch.object(sys, "argv", self._given_command_line()):
            kwargs = {
                "cmd_ps": entry_point_under_test,
            }
            self._test_process(**kwargs)

    def _test_process(self, cmd_ps: Callable):
        mock_parser_arg = self._given_parser_args()
        command = _given_command(app_type="Python web library")
        command.run = MagicMock()
        cmd_parser = Mock()

        with patch.object(WSGIServer, "generate", return_value=command) as mock_sgi_generate:
            cmd_ps(cmd_parser, mock_parser_arg)
            mock_sgi_generate.assert_not_called()
            command.run.assert_not_called()

    def _given_parser_args(self) -> ParserArguments:
        return ParserArguments(
            subparser_structure=SysArg.parse([]),
        )

    def _given_command_line(self) -> List[str]:
        return []

    def _given_cmd_args_namespace(self) -> Namespace:
        args_namespace = Namespace()
        args_namespace.subcommand = None
        return args_namespace

    def _given_subcmd(self) -> Optional[SysArg]:
        return SysArg(subcmd=SubCommandLine.Base)

    def _expected_argument_type(self) -> Type[Namespace]:
        return Namespace


def test_make_command_chain():
    assert len(get_all_subcommands()) == len(make_command_chain()) - _No_SubCmd_Amt - _Fake_Amt


def test_make_command_chain_if_duplicated_subcmd():
    class FakeCmdPS(BaseCommandProcessor):
        responsible_subcommand: SysArg = _Fake_Duplicated_SubCmd_Obj

        def run(self, args: ParserArguments) -> None:
            pass

    class FakeDuplicatedCmdPS(BaseCommandProcessor):
        responsible_subcommand: SysArg = _Fake_Duplicated_SubCmd_Obj

        def run(self, args: ParserArguments) -> None:
            pass

    with pytest.raises(ValueError) as exc_info:
        make_command_chain()
    assert re.search(r"subcommand.{1,64}has been used", str(exc_info.value), re.IGNORECASE)

    # Remove the invalid object for test could run finely.
    from pymock_server.command._base.process import CommandProcessChain

    CommandProcessChain.pop(-1)
