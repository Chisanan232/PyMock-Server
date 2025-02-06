import os
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import List, Optional

try:
    from fake_api_server.command._base.process import CommandProcessor
    from fake_api_server.command.process import dispatch_command_processor
    from fake_api_server.model import ParserArguments
except ImportError:
    runner_dir = os.path.dirname(os.path.abspath(__file__))
    path = str(Path(runner_dir).parent.absolute())
    sys.path.append(path)
    from fake_api_server.command.process import (
        CommandProcessor,
        dispatch_command_processor,
    )
    from fake_api_server.model import ParserArguments


class CommandRunner:
    def __init__(self):
        self._cmd_processor = self._dispatch()
        self.cmd_parser: ArgumentParser = self._cmd_processor.fake_api_server_parser.parse()

    def run(self, cmd_args: ParserArguments) -> None:
        self._cmd_processor.process(parser=self.cmd_parser, args=cmd_args)

    def parse(self, cmd_args: Optional[List[str]] = None) -> ParserArguments:
        return self._cmd_processor.parse(parser=self.cmd_parser, cmd_args=cmd_args)

    def _dispatch(self) -> CommandProcessor:
        return dispatch_command_processor()


def run() -> None:
    cmd_runner = CommandRunner()
    arguments = cmd_runner.parse()
    cmd_runner.run(arguments)


if __name__ == "__main__":
    run()
