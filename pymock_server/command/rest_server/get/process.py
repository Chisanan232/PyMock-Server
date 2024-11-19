from argparse import ArgumentParser
from typing import List, Optional

from pymock_server.command._base_process import BaseCommandProcessor
from pymock_server.command.subcommand import SubCommandLine
from pymock_server.model import SubcmdGetArguments, deserialize_args
from pymock_server.model.subcmd_common import SysArg

from .component import SubCmdGetComponent


class SubCmdGet(BaseCommandProcessor):
    responsible_subcommand: SysArg = SysArg(
        pre_subcmd=SysArg(pre_subcmd=SysArg(subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer),
        subcmd=SubCommandLine.Get,
    )

    @property
    def _subcmd_component(self) -> SubCmdGetComponent:
        return SubCmdGetComponent()

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> SubcmdGetArguments:
        return deserialize_args.subcmd_get(self._parse_cmd_arguments(parser, cmd_args))
