import os
import re
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List, Optional, Union

try:
    import pymock_api.cmd
    import pymock_api.cmd_ps
    from pymock_api._utils.file_opt import YAML
    from pymock_api.model import (
        ParserArguments,
        SubcmdConfigArguments,
        SubcmdRunArguments,
        deserialize_args,
    )
    from pymock_api.model._sample import Sample_Config_Value
    from pymock_api.server import BaseSGIServer, setup_asgi, setup_wsgi
except (ImportError, ModuleNotFoundError):
    runner_dir = os.path.dirname(os.path.abspath(__file__))
    path = str(Path(runner_dir).parent.absolute())
    sys.path.append(path)
    import pymock_api.cmd
    import pymock_api.cmd_ps
    from pymock_api._utils.file_opt import YAML
    from pymock_api.model import (
        ParserArguments,
        SubcmdConfigArguments,
        SubcmdRunArguments,
        deserialize_args,
    )
    from pymock_api.model._sample import Sample_Config_Value
    from pymock_api.server import BaseSGIServer, setup_asgi, setup_wsgi


class CommandRunner:
    def __init__(self):
        self.mock_api_parser = pymock_api.cmd.MockAPICommandParser()
        self.cmd_parser: ArgumentParser = self.mock_api_parser.parse()
        self._server_gateway: BaseSGIServer = None

    def run(self, cmd_args: ParserArguments) -> None:
        pymock_api.cmd_ps.run_command_chain(cmd_args)

    def parse(self, cmd_args: Optional[List[str]] = None) -> Union[SubcmdRunArguments, SubcmdConfigArguments]:
        if self.mock_api_parser.subcommand == pymock_api.cmd.SubCommand.Run:
            return self.parse_subcmd_run(cmd_args)
        elif self.mock_api_parser.subcommand == pymock_api.cmd.SubCommand.Config:
            return self.parse_subcmd_config(cmd_args)
        else:
            return self._parse_cmd_arguments(cmd_args)

    def parse_subcmd_run(self, cmd_args: Optional[List[str]] = None) -> SubcmdRunArguments:
        return deserialize_args.subcmd_run(self._parse_cmd_arguments(cmd_args))

    def parse_subcmd_config(self, cmd_args: Optional[List[str]] = None) -> SubcmdConfigArguments:
        return deserialize_args.subcmd_config(self._parse_cmd_arguments(cmd_args))

    def _parse_cmd_arguments(self, cmd_args: Optional[List[str]] = None) -> Namespace:
        return self.cmd_parser.parse_args(cmd_args)


def run() -> None:
    cmd_runner = CommandRunner()
    arguments = cmd_runner.parse()
    cmd_runner.run(arguments)


if __name__ == "__main__":

    run()
