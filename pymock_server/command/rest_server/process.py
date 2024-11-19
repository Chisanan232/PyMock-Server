from argparse import ArgumentParser
from typing import List, Optional

from pymock_server.command._base._base_process import BaseCommandProcessor
from pymock_server.command.subcommand import SubCommandLine
from pymock_server.model import ParserArguments
from pymock_server.model.subcmd_common import SysArg

from .component import SubCmdRestServerComponent


class SubCmdRestServer(BaseCommandProcessor):
    responsible_subcommand: SysArg = SysArg(
        pre_subcmd=SysArg(subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer
    )

    @property
    def _subcmd_component(self) -> SubCmdRestServerComponent:
        return SubCmdRestServerComponent()

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> ParserArguments:
        return self._parse_cmd_arguments(parser, cmd_args)
