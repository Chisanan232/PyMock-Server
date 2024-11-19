from argparse import ArgumentParser
from typing import List, Optional

from pymock_server.model import ParserArguments
from pymock_server.model.subcmd_common import SysArg

from ._base import BaseAutoLoad
from ._base.process import BaseCommandProcessor, CommandProcessChain, CommandProcessor
from .component import NoSubCmdComponent
from .subcommand import SubCommandLine

_Subcommand_Interface: List[SubCommandLine] = [SubCommandLine.RestServer]


class AutoLoadProcessor(BaseAutoLoad):
    py_module: str = "process.py"
    _current_module: str = __file__

    def _wrap_as_object_name(self, subcmd_object: str) -> str:
        return f"SubCmd{subcmd_object}"


AutoLoadProcessor().import_all()


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
