"""*The command attributes of PyFake-API-Server*

This module processes the features about command to let *PyFake-API-Server* could be used and run through command line.
In briefly, It has below major features:

* Parser of *PyFake-API-Server* command line
  Handling parsing the arguments of command line.

* Options of *PyFake-API-Server* command
  Handling all the details of command options, i.e., what the option format should be used in command line, the help
  description of what this option does, etc.

"""

import argparse
import logging
from importlib.metadata import PackageNotFoundError, version
from typing import Any, List

from fake_api_server.__pkg_info__ import __version__
from fake_api_server.model.subcmd_common import SubCommandAttr

from .._utils.importing import SUPPORT_SGI_SERVER, SUPPORT_WEB_FRAMEWORK
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
    fake_api_server_cmd_options: List["CommandOption"] = []
    for option_cls in CommandLineOptions.get():
        option = option_cls()
        if not option.cli_option:
            raise ValueError(f"The object {option.__class__}'s attribute *cli_option* cannot be None or empty value.")
        fake_api_server_cmd_options.append(option.copy())
    return fake_api_server_cmd_options


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


BaseCmdOption: type = MetaCommandOption("BaseCmdOption", (BaseSubCommand,), {})


class Version(BaseCmdOption):
    cli_option: str = "-v, --version"
    name: str = "version"
    help_description: str = "The version info of PyFake-API-Server."
    default_value: Any = argparse.SUPPRESS
    action: str = "version"

    @property
    def _version_output(self) -> str:

        def _get_version(py_pkg: str) -> str:
            try:
                return version(py_pkg)
            except PackageNotFoundError:
                return ""

        def _generate_version_info(support_py_pkg: List[str]) -> str:
            _version_info = ""
            for py_pkg in support_py_pkg:
                py_pkg_ver = _get_version(py_pkg)
                if py_pkg_ver:
                    _version_info += f"{py_pkg} (version: {py_pkg_ver})\n"
            return _version_info

        web_server_ver_info = _generate_version_info(support_py_pkg=SUPPORT_WEB_FRAMEWORK)
        sgi_ver_info = _generate_version_info(support_py_pkg=SUPPORT_SGI_SERVER)

        return (
            f"######## PyFake-API-Server: #########\n"
            f"%(prog)s (version {__version__})\n\n"
            f"############ Web server: ############\n"
            f"{web_server_ver_info}\n"
            f"#### Server gateway interface: ######\n"
            f"{sgi_ver_info}"
        )

    def add_option(self, parser: argparse.ArgumentParser) -> None:
        cmd_option_args = {
            "dest": self.name,
            "help": self.help_description,
            "default": self.default_value,
            "action": self.action or "store",
            "version": self._version_output,
        }
        parser.add_argument(*self.cli_option_name, **cmd_option_args)
