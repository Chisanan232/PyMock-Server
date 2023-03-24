from argparse import Namespace
from typing import Type
from unittest.mock import Mock, patch

import pytest

from pymock_api.server.sgi._model import (
    Command,
    CommandOptions,
    Deserialize,
    ParserArguments,
)

from ...._values import (
    _Bind_Host_And_Port,
    _Cmd_Option,
    _Log_Level,
    _Test_App_Type,
    _Test_Config,
    _Test_Entry_Point,
    _Test_SubCommand,
    _Workers_Amount,
)


def _generate_cmd_option(option: _Cmd_Option) -> str:
    return f"{option.option_name} {option.value}"


def _get_cmd_options() -> (str, str, str):
    host_and_port = _generate_cmd_option(_Bind_Host_And_Port)
    workers = _generate_cmd_option(_Workers_Amount)
    log_level = _generate_cmd_option(_Log_Level)
    return host_and_port, workers, log_level


class TestCommandOptions:
    @pytest.fixture(scope="function")
    def command_options(self) -> CommandOptions:
        host_and_port, workers, log_level = _get_cmd_options()
        return CommandOptions(bind=host_and_port, workers=workers, log_level=log_level)

    def test_str(self, command_options: CommandOptions):
        options = str(command_options)
        host_and_port, workers, log_level = _get_cmd_options()
        expected_options = " ".join([host_and_port, workers, log_level])
        assert options == expected_options, "The string value should be the same."

    def test_all_options(self, command_options: CommandOptions):
        host_and_port, workers, log_level = _get_cmd_options()
        assert command_options.all_options == [
            host_and_port,
            workers,
            log_level,
        ], "The list value of all options should be the same."


class TestCommand:
    Web_Lib_Name = "python web library name"

    @pytest.fixture(scope="function")
    def command(self) -> Command:
        host_and_port, workers, log_level = _get_cmd_options()
        return Command(
            entry_point=_Test_Entry_Point,
            app="application instance path",
            options=CommandOptions(bind=host_and_port, workers=workers, log_level=log_level),
        )

    def test_line(self, command: Command):
        expected_cmd = TestCommand.expected_cmd_line(command)
        assert command.line == expected_cmd

    @patch("subprocess.run")
    def test_run(self, mock_subprocess_run: Mock, command: Command):
        expected_cmd = TestCommand.expected_cmd_line(command)
        command.run()
        mock_subprocess_run.assert_called_once_with(expected_cmd, shell=True)

    @classmethod
    def expected_cmd_line(cls, command: Command) -> str:
        host_and_port, workers, log_level = _get_cmd_options()
        return " ".join([command.entry_point, host_and_port, workers, log_level, command.app_path])


class TestDeserialize:
    @pytest.fixture(scope="function")
    def deserialize(self) -> Type[Deserialize]:
        return Deserialize

    def test_parser_arguments(self, deserialize: Type[Deserialize]):
        namespace_args = {
            _Test_SubCommand: _Test_SubCommand,
            "config": _Test_Config,
            "app_type": _Test_App_Type,
            "bind": _Bind_Host_And_Port.value,
            "workers": _Workers_Amount.value,
            "log_level": _Log_Level.value,
        }
        namespace = Namespace(**namespace_args)
        arguments = deserialize.parser_arguments(namespace, subcmd=_Test_SubCommand)
        assert isinstance(arguments, ParserArguments)
        assert arguments.subparser_name == _Test_SubCommand
        assert arguments.config == _Test_Config
        assert arguments.app_type == _Test_App_Type
        assert arguments.bind == _Bind_Host_And_Port.value
        assert arguments.workers == _Workers_Amount.value
        assert arguments.log_level == _Log_Level.value
