import logging
import sys
from argparse import Namespace

from pymock_server.command._base.process import BaseCommandProcessor
from pymock_server.command.subcommand import SubCommandLine
from pymock_server.model import SubcmdSampleArguments, deserialize_args
from pymock_server.model.subcmd_common import SysArg

from .component import SubCmdSampleComponent

logger = logging.getLogger(__name__)


class SubCmdSample(BaseCommandProcessor):
    responsible_subcommand: SysArg = SysArg(
        pre_subcmd=SysArg(pre_subcmd=SysArg(subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer),
        subcmd=SubCommandLine.Sample,
    )

    @property
    def _subcmd_component(self) -> SubCmdSampleComponent:
        return SubCmdSampleComponent()

    def _parse_process(self, args: Namespace) -> SubcmdSampleArguments:
        try:
            return deserialize_args.cli_rest_server.subcmd_sample(args)
        except KeyError:
            logger.error(f"❌  Invalid value of option *--sample-config-type*: {args.sample_config_type}.")
            sys.exit(1)
