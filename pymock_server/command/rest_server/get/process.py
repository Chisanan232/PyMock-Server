from argparse import Namespace

from pymock_server.command._base.process import BaseCommandProcessor
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

    def _parse_process(self, args: Namespace) -> SubcmdGetArguments:
        return deserialize_args.subcmd_get(args)
