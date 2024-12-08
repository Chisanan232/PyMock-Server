from argparse import ArgumentParser
from typing import List, Optional

from pymock_server.command._base.process import BaseCommandProcessor
from pymock_server.command.subcommand import SubCommandLine
from pymock_server.model import SubcmdPullArguments, deserialize_args
from pymock_server.model.subcmd_common import SysArg

from .component import SubCmdPullComponent


class SubCmdPull(BaseCommandProcessor):
    responsible_subcommand: SysArg = SysArg(
        pre_subcmd=SysArg(pre_subcmd=SysArg(subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer),
        subcmd=SubCommandLine.Pull,
    )

    @property
    def _subcmd_component(self) -> SubCmdPullComponent:
        return SubCmdPullComponent()

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> SubcmdPullArguments:
        return deserialize_args.subcmd_pull(self._parse_cmd_arguments(parser, cmd_args))
