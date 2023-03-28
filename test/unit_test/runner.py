import argparse
from typing import Callable
from unittest.mock import MagicMock, Mock, patch

import pytest

from pymock_api.model import deserialize_args
from pymock_api.model.cmd_args import SubcmdRunArguments
from pymock_api.runner import CommandRunner, run
from pymock_api.server.sgi import WSGIServer
from pymock_api.server.sgi._model import Command, CommandOptions

from .._sut import get_runner
from .._values import (
    _Bind_Host_And_Port,
    _Log_Level,
    _Test_App_Type,
    _Test_Config,
    _Test_SubCommand_Run,
    _Workers_Amount,
)

MOCK_ARGS_PARSE_RESULT = Mock()


def _given_parser_args(subcommand: str = None, app_type: str = None) -> SubcmdRunArguments:
    return SubcmdRunArguments(
        subparser_name=subcommand,
        app_type=app_type,
        config=_Test_Config,
        bind=_Bind_Host_And_Port.value,
        workers=_Workers_Amount.value,
        log_level=_Log_Level.value,
    )


def _given_command_option() -> CommandOptions:
    return CommandOptions(bind=_Bind_Host_And_Port.value, workers=_Workers_Amount.value, log_level=_Log_Level.value)


def _given_command(app_type: str) -> Command:
    mock_parser_arg = _given_parser_args(app_type)
    mock_cmd_option_obj = _given_command_option()
    return Command(entry_point="SGI tool command", app=mock_parser_arg.app_type, options=mock_cmd_option_obj)


class FakeRunner(CommandRunner):
    def __init__(self):
        pass


class TestEntryPoint:
    def test_run(self):
        def _give() -> SubcmdRunArguments:
            return _given_parser_args(app_type=_Test_App_Type)

        def _run_sut() -> None:
            run()

        def _should_be_called_as(instantiate_runner: Mock, parse_func: Mock, run_app_func: Mock) -> None:
            instantiate_runner.assert_called_once()
            parse_func.assert_called_once()
            run_app_func.assert_not_called()

        self._run_test_within_mock(given=_give, run_uat=_run_sut, should_be=_should_be_called_as)

    def test_run_with_subcommand_run(self):
        mock_parser_arg: SubcmdRunArguments = None

        def _give() -> SubcmdRunArguments:
            nonlocal mock_parser_arg
            mock_parser_arg = _given_parser_args(subcommand=_Test_SubCommand_Run, app_type=_Test_App_Type)
            return mock_parser_arg

        def _run_sut() -> None:
            run()

        def _should_be_called_as(instantiate_runner: Mock, parse_func: Mock, run_app_func: Mock) -> None:
            instantiate_runner.assert_called_once()
            parse_func.assert_called_once()
            run_app_func.assert_called_once_with(mock_parser_arg)

        self._run_test_within_mock(given=_give, run_uat=_run_sut, should_be=_should_be_called_as)

    @classmethod
    def _run_test_within_mock(cls, given: Callable, run_uat: Callable, should_be: Callable) -> None:
        mock_parser_arg = given()
        fake_runner = FakeRunner()
        with patch("pymock_api.runner.CommandRunner", return_value=fake_runner) as mock_runner_instance:
            with patch.object(fake_runner, "parse", return_value=mock_parser_arg) as mock_parse:
                with patch.object(fake_runner, "run_app") as mock_run_app:
                    run_uat()
                    should_be(mock_runner_instance, mock_parse, mock_run_app)


class TestCommandRunner:
    @pytest.fixture(scope="function")
    def runner(self) -> CommandRunner:
        return get_runner()

    def test_run_app(self, runner: CommandRunner):
        mock_parser_arg = _given_parser_args(app_type=_Test_App_Type)
        command = _given_command(app_type="Python web library")
        command.run = MagicMock()

        with patch.object(WSGIServer, "generate", return_value=command) as mock_sgi_generate:
            runner.run_app(mock_parser_arg)
            mock_sgi_generate.assert_called_once_with(mock_parser_arg)
            command.run.assert_called_once()

    def test_bad_run_app(self, runner: CommandRunner):
        mock_parser_arg = _given_parser_args(app_type="invalid app-type which is not a Python web library or framework")
        command = _given_command(app_type="Python web library")
        command.run = MagicMock()

        with patch.object(WSGIServer, "generate", return_value=command) as mock_sgi_generate:
            with pytest.raises(ValueError) as exc_info:
                runner.run_app(mock_parser_arg)
            assert "Invalid value" in str(exc_info.value)
            mock_sgi_generate.assert_not_called()
            command.run.assert_not_called()

    @patch.object(argparse.ArgumentParser, "parse_args", return_value=MOCK_ARGS_PARSE_RESULT)
    @patch.object(deserialize_args, "subcmd_run")
    def test_parse(self, mock_deserialize: Mock, mock_parse_args: Mock, runner: CommandRunner):
        runner.parse_subcmd_run()

        mock_parse_args.assert_called_once_with(None)
        mock_deserialize.assert_called_once_with(MOCK_ARGS_PARSE_RESULT)
