from argparse import ArgumentParser
from typing import List, Optional

from pymock_server.model import ParserArguments
from pymock_server.model.subcmd_common import SysArg

from ._base_process import BaseCommandProcessor, CommandProcessChain, CommandProcessor
from .component import NoSubCmdComponent

# FIXME: Please remove below imports after refactoring done
from .rest_server.add.process import import_add_process
from .rest_server.check.process import import_process as import_check_process
from .rest_server.get.process import import_process as import_get_process
from .rest_server.process import import_option
from .rest_server.pull.process import import_process as import_pull_process
from .rest_server.run.process import import_process as import_run_process
from .rest_server.sample.process import import_process as import_sample_process
from .subcommand import SubCommandLine

# FIXME: Please use more clear and beautiful implementation to apply the command line options
import_option()
import_add_process()
import_check_process()
import_get_process()
import_pull_process()
import_run_process()
import_sample_process()


def dispatch_command_processor() -> "CommandProcessor":
    cmd_chain = make_command_chain()
    assert len(cmd_chain) > 0, "It's impossible that command line processors list is empty."
    return cmd_chain[0].distribute()


def run_command_chain(parser: ArgumentParser, args: ParserArguments) -> None:
    cmd_chain = make_command_chain()
    assert len(cmd_chain) > 0, "It's impossible that command line processors list is empty."
    cmd_chain[0].process(parser=parser, args=args)


def make_command_chain() -> List["CommandProcessor"]:
    existed_subcmd: List[Optional[SysArg]] = []
    mock_api_cmd: List["CommandProcessor"] = []
    for cmd_cls in CommandProcessChain.get():
        cmd = cmd_cls()
        if cmd.responsible_subcommand in existed_subcmd:
            raise ValueError(f"The subcommand *{cmd.responsible_subcommand}* has been used. Please use other naming.")
        existed_subcmd.append(getattr(cmd, "responsible_subcommand"))
        mock_api_cmd.append(cmd.copy())
    return mock_api_cmd


class NoSubCmd(BaseCommandProcessor):
    responsible_subcommand: SysArg = SysArg(subcmd=SubCommandLine.Base)

    @property
    def _subcmd_component(self) -> NoSubCmdComponent:
        return NoSubCmdComponent()

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> ParserArguments:
        return self._parse_cmd_arguments(parser, cmd_args)
