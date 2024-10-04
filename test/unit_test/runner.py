from unittest.mock import Mock, patch

import pytest

from pymock_server.model.cmd_args import ParserArguments
from pymock_server.runner import CommandRunner, run

MOCK_ARGS_PARSE_RESULT = Mock()


class TestEntryPoint:
    @pytest.fixture(scope="function")
    def runner(self) -> CommandRunner:
        return CommandRunner()

    def test_run(self, runner: CommandRunner):
        mock_parser_arg = ParserArguments(subparser_name=None)
        with patch("pymock_server.runner.CommandRunner", return_value=runner) as mock_runner_instance:
            with patch.object(runner, "parse", return_value=mock_parser_arg) as mock_parse:
                with patch.object(runner, "run") as mock_run:
                    run()

                    mock_runner_instance.assert_called_once()
                    mock_parse.assert_called_once()
                    mock_run.assert_called_once_with(mock_parser_arg)
