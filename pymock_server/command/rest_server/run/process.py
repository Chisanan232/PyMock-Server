from argparse import Namespace

from pymock_server.command._base.process import BaseCommandProcessor
from pymock_server.command.subcommand import SubCommandLine
from pymock_server.model import SubcmdRunArguments, deserialize_args
from pymock_server.model.subcmd_common import SysArg

from .component import SubCmdRunComponent


class SubCmdRun(BaseCommandProcessor):
    responsible_subcommand: SysArg = SysArg(
        pre_subcmd=SysArg(pre_subcmd=SysArg(subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer),
        subcmd=SubCommandLine.Run,
    )

    @property
    def _subcmd_component(self) -> SubCmdRunComponent:
        return SubCmdRunComponent()

    def _parse_process(self, args: Namespace) -> SubcmdRunArguments:
        return deserialize_args.subcmd_run(args)
