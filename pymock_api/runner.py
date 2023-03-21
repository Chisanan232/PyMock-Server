import os
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
        self.parser = pymock_api.cmd.MockAPICommandParser()
        self.sgi_cmd: WSGICmd = None

    def run(self, args: ParserArguments) -> None:
        command = self.sgi_cmd.generate(args)
        command.run()

    def parse(self, cmd_args: List[str] = None) -> ParserArguments:
        args = self._load_parser(cmd_args)
        parser_options = deserialize_parser_args(args)
        self._process_option(parser_options)
        return parser_options

    def _load_parser(self, cmd_args=None) -> Namespace:
        parser = self.parser.parse()
        args = parser.parse_args(cmd_args)
        return args

    def _process_option(self, parser_options: ParserArguments) -> None:
        # Note: It's possible that it should separate the functions to be multiple objects to implement and manage the
        # behaviors of command line with different options.
        # Handle *config*
        os.environ["MockAPI_Config"] = parser_options.config

        # Handle *app-type*
        if parser_options.app_type == "flask":
            self.sgi_cmd = WSGICmd()
        else:
            raise ValueError("Invalid value at argument *app-type*. It only supports 'fldask' currently.")


def run() -> None:
    cmd_runner = CommandRunner()
    arguments = cmd_runner.parse()
    cmd_runner.run(arguments)


if __name__ == "__main__":

    run()
