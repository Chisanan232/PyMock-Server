"""*The command attributes of PyMock-API*

This module processes the features about command to let *PyMock-API* could be used and run through command line. In
briefly, It has below major features:

* Parser of *PyMock-API* command line
  Handling parsing the arguments of command line.

* Options of *PyMock-API* command
  Handling all the details of command options, i.e., what the option format should be used in command line, the help
  description of what this option does, etc.

"""

import argparse
import glob
import logging
import os
import pathlib
from typing import Any, List

from pymock_server.__pkg_info__ import __version__
from pymock_server.model.subcmd_common import SubCommandAttr

from ._base_options import (
    CommandLineOptions,
    CommandOption,
    MetaCommandOption,
    SubCommandInterface,
)
from .subcommand import SubCommandLine, SubCommandSection

logger = logging.getLogger(__name__)

_Subcommand_Interface: List[SubCommandLine] = [SubCommandLine.RestServer]


def import_subcommand_option() -> None:
    for subcmd_inf in list(map(lambda e: e.value.replace("-", "_"), _Subcommand_Interface)):
        cmd_module_path = pathlib.Path(__file__).parent.absolute()
        subcmd_inf_pkg_path = pathlib.Path(cmd_module_path, subcmd_inf, "**")
        for subcmd_dir in glob.glob(str(subcmd_inf_pkg_path)):
            if os.path.isdir(subcmd_dir):
                subcmd_options_module = pathlib.Path(f"{subcmd_dir}", "options.py")
                if os.path.exists(str(subcmd_options_module)):
                    # convert the file path as Python importing
                    import_style = str(subcmd_options_module).replace(".py", "").replace("/", ".")
                    lib_name = "pymock_server"
                    subcmd_sub_pkg_name = pathlib.Path(subcmd_dir).name
                    import_abs_path = ".".join([lib_name, import_style.split(f"{lib_name}.")[1]])
                    subcmd_option_obj = f"SubCommand{subcmd_sub_pkg_name[0].upper() + subcmd_sub_pkg_name[1:]}Option"
                    exec(f"from {import_abs_path} import {subcmd_option_obj}")


import_subcommand_option()

"""
Common functon about command line option
"""


def get_all_subcommands() -> List[str]:
    return list(set(SubCommandInterface.get()))


def make_options() -> List["CommandOption"]:
    """Initial and generate all options for parser to use and organize.

    Returns:
        list: A list object of **CommandOption** objects.

    """
    mock_api_cmd_options: List["CommandOption"] = []
    for option_cls in CommandLineOptions.get():
        option = option_cls()
        if not option.cli_option:
            raise ValueError(f"The object {option.__class__}'s attribute *cli_option* cannot be None or empty value.")
        mock_api_cmd_options.append(option.copy())
    return mock_api_cmd_options


"""
Command line options for first layer command line (without any subcommand line).
"""


class BaseSubCommand(CommandOption):
    sub_cmd: SubCommandAttr = SubCommandAttr(
        title=SubCommandSection.Base,
        dest=SubCommandLine.Base,
        description="",
        help="",
    )


BaseCmdOption: type = MetaCommandOption("BaseCmdOption", (CommandOption,), {})


class Version(BaseCmdOption):
    cli_option: str = "-v, --version"
    name: str = "version"
    help_description: str = "The version info of PyMock-API."
    default_value: Any = argparse.SUPPRESS
    action: str = "version"
    _version_output: str = "%(prog)s (version " + __version__ + ")\n"

    def add_option(self, parser: argparse.ArgumentParser) -> None:
        # TODO: Should get relation tools or library's version, e.g., flask, gunicorn, etc.
        cmd_option_args = {
            "dest": self.name,
            "help": self.help_description,
            "default": self.default_value,
            "action": self.action or "store",
            "version": self._version_output,
        }
        parser.add_argument(*self.cli_option_name, **cmd_option_args)
