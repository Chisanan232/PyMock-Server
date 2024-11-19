from argparse import ArgumentParser
from typing import List, Optional

from pymock_server.command._base.process import BaseCommandProcessor
from pymock_server.command.subcommand import SubCommandLine
from pymock_server.model import SubcmdCheckArguments, deserialize_args
from pymock_server.model.subcmd_common import SysArg

from .component import SubCmdCheckComponent


class SubCmdCheck(BaseCommandProcessor):
    responsible_subcommand: SysArg = SysArg(
        pre_subcmd=SysArg(pre_subcmd=SysArg(subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer),
        subcmd=SubCommandLine.Check,
    )

    @property
    def _subcmd_component(self) -> SubCmdCheckComponent:
        return SubCmdCheckComponent()

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> SubcmdCheckArguments:
        return deserialize_args.subcmd_check(self._parse_cmd_arguments(parser, cmd_args))
