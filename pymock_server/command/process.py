import glob
import pathlib
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

    @classmethod
    def import_all(cls) -> None:
        for subcmd_inf in list(map(lambda e: e.value.replace("-", "_"), _Subcommand_Interface)):
            subcmd_inf_pkg_path = cls._regex_module_paths(subcmd_inf)
            for subcmd_ps_module_file_path in glob.glob(str(subcmd_inf_pkg_path), recursive=True):
                # convert the file path as Python importing
                # module path
                import_abs_path = cls._to_import_module_path(subcmd_ps_module_file_path)

                # object
                subcmd_option_obj = cls._to_subcmd_object(subcmd_ps_module_file_path)

                # import the object from the module path
                exec(f"from {import_abs_path} import {subcmd_option_obj}")

    @classmethod
    def _to_subcmd_object(cls, subcmd_ps_module_file_path: str) -> str:
        subcmd_dir = pathlib.Path(subcmd_ps_module_file_path).parent.name
        subcmd_sub_pkg_name_parts = subcmd_dir.split("_")
        subcmd_option_obj: str = "SubCmd"
        for part in subcmd_sub_pkg_name_parts:
            subcmd_option_obj += part[0].upper() + part[1:]
        return subcmd_option_obj

    @classmethod
    def _to_import_module_path(cls, subcmd_ps_module_file_path: str) -> str:
        import_style = subcmd_ps_module_file_path.replace(".py", "").replace("/", ".")
        lib_name = "pymock_server"
        import_abs_path = ".".join([lib_name, import_style.split(f"{lib_name}.")[1]])
        return import_abs_path

    @classmethod
    def _regex_module_paths(cls, subcmd_inf: str) -> pathlib.Path:
        cmd_module_path = pathlib.Path(__file__).parent.absolute()
        assert cls.py_module, "Python module name must not be empty."
        subcmd_inf_pkg_path = pathlib.Path(cmd_module_path, subcmd_inf, "**", cls.py_module)
        return subcmd_inf_pkg_path


AutoLoadProcessor.import_all()


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
