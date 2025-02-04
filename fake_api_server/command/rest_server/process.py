from argparse import Namespace

from fake_api_server.command._base.process import BaseCommandProcessor
from fake_api_server.command.subcommand import SubCommandLine
from fake_api_server.model.subcmd_common import SysArg

from .component import SubCmdRestServerComponent


class SubCmdRestServer(BaseCommandProcessor):
    responsible_subcommand: SysArg = SysArg(
        pre_subcmd=SysArg(subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer
    )

    @property
    def _subcmd_component(self) -> SubCmdRestServerComponent:
        return SubCmdRestServerComponent()

    def _parse_process(self, args: Namespace) -> Namespace:
        return args
