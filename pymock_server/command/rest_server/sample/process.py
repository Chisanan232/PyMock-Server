import logging
import sys
from argparse import ArgumentParser
from typing import List, Optional

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

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> SubcmdSampleArguments:
        cmd_options = self._parse_cmd_arguments(parser, cmd_args)
        try:
            return deserialize_args.subcmd_sample(cmd_options)
        except KeyError:
            logger.error(f"❌  Invalid value of option *--sample-config-type*: {cmd_options.sample_config_type}.")
            sys.exit(1)
