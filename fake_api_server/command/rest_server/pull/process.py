from argparse import Namespace

from fake_api_server.command._base.process import BaseCommandProcessor
from fake_api_server.command.subcommand import SubCommandLine
from fake_api_server.model import SubcmdPullArguments, deserialize_args
from fake_api_server.model.subcmd_common import SysArg

from .component import SubCmdPullComponent


class SubCmdPull(BaseCommandProcessor):
    responsible_subcommand: SysArg = SysArg(
        pre_subcmd=SysArg(pre_subcmd=SysArg(subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer),
        subcmd=SubCommandLine.Pull,
    )

    @property
    def _subcmd_component(self) -> SubCmdPullComponent:
        return SubCmdPullComponent()

    def _parse_process(self, args: Namespace) -> SubcmdPullArguments:
        return deserialize_args.cli_rest_server.subcmd_pull(args)
