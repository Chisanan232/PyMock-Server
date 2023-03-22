import os
import re
import sys
from argparse import Namespace
from pathlib import Path
from typing import List

try:
    import pymock_api.cmd
    from pymock_api.server.sgi import ParserArguments, WSGICmd, deserialize_parser_args
except (ImportError, ModuleNotFoundError):
    runner_dir = os.path.dirname(os.path.abspath(__file__))
    path = str(Path(runner_dir).parent.absolute())
    sys.path.append(path)
    import pymock_api.cmd
    from pymock_api.server.sgi import ParserArguments, WSGICmd, deserialize_parser_args


class CommandRunner:
    def __init__(self):
        self.mock_api_parser = pymock_api.cmd.MockAPICommandParser()
        self.cmd_parser = self.mock_api_parser.parse()
        self.sgi_cmd: WSGICmd = None

    def run_app(self, args: ParserArguments) -> None:
        self._process_option(args)
        command = self.sgi_cmd.generate(args)
        command.run()

    def parse(self, cmd_args: List[str] = None) -> ParserArguments:
        args = self._parse_cmd_arguments(cmd_args)
        parser_options = deserialize_parser_args(args, subcmd=self.mock_api_parser.subcommand)
        return parser_options

    def _parse_cmd_arguments(self, cmd_args: List[str]) -> Namespace:
        return self.cmd_parser.parse_args(cmd_args)

    def _process_option(self, parser_options: ParserArguments) -> None:
        # Note: It's possible that it should separate the functions to be multiple objects to implement and manage the
        # behaviors of command line with different options.
        # Handle *config*
        os.environ["MockAPI_Config"] = parser_options.config

        # Handle *app-type*
        if re.search(r"flask", parser_options.app_type, re.IGNORECASE):
            self.sgi_cmd = WSGICmd()
        else:
            raise ValueError("Invalid value at argument *app-type*. It only supports 'flask' currently.")


def run() -> None:
    cmd_runner = CommandRunner()
    arguments = cmd_runner.parse()
    if arguments.subparser_name == pymock_api.cmd.SubCommand.Run:
        cmd_runner.run_app(arguments)


if __name__ == "__main__":

    run()
