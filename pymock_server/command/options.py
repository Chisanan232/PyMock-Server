"""*The command attributes of PyMock-Server*

This module processes the features about command to let *PyMock-Server* could be used and run through command line. In
briefly, It has below major features:

* Parser of *PyMock-Server* command line
  Handling parsing the arguments of command line.

* Options of *PyMock-Server* command
  Handling all the details of command options, i.e., what the option format should be used in command line, the help
  description of what this option does, etc.

"""

import argparse
import logging
from typing import Any, List

from pymock_server.__pkg_info__ import __version__
from pymock_server.model.subcmd_common import SubCommandAttr

from ._base import BaseAutoLoad
from ._base.options import (
    CommandLineOptions,
    CommandOption,
    MetaCommandOption,
    SubCommandInterface,
)
from .subcommand import SubCommandLine, SubCommandSection

logger = logging.getLogger(__name__)

_Subcommand_Interface: List[SubCommandLine] = [SubCommandLine.RestServer]


class AutoLoadOptions(BaseAutoLoad):
    _current_module: str = __file__

    def _wrap_as_object_name(self, subcmd_object: str) -> str:
        return f"SubCommand{subcmd_object}Option"


AutoLoadOptions().import_all()

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
    help_description: str = "The version info of PyMock-Server."
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
