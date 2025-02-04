from argparse import Namespace

from fake_api_server.command._base.process import BaseCommandProcessor
from fake_api_server.command.subcommand import SubCommandLine
from fake_api_server.model import SubcmdCheckArguments, deserialize_args
from fake_api_server.model.subcmd_common import SysArg

from .component import SubCmdCheckComponent


class SubCmdCheck(BaseCommandProcessor):
    responsible_subcommand: SysArg = SysArg(
        pre_subcmd=SysArg(pre_subcmd=SysArg(subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer),
        subcmd=SubCommandLine.Check,
    )

    @property
    def _subcmd_component(self) -> SubCmdCheckComponent:
        return SubCmdCheckComponent()

    def _parse_process(self, args: Namespace) -> SubcmdCheckArguments:
        return deserialize_args.cli_rest_server.subcmd_check(args)
