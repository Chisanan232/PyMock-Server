import argparse
import sys
from typing import Any, Dict, List, Optional

from fake_api_server.command._base.options import CommandOption
from fake_api_server.model.subcmd_common import SysArg

from .options import get_all_subcommands, make_options


class FakeAPIServerCommandParser:
    """*The parser of PyFake-API-Server command line*

    Handling the command line about options includes what options PyFake-API-Server could use and what values of entry
    command line.
    """

    def __init__(self):
        self._prog = "pyfake-api-server"
        self._usage = "fake" if self.is_running_subcmd else "fake [<API server>] [subcommand] [options]"
        self._description = """
        A Python tool for faking APIs by set up an application easily. PyFake-API-Server bases on Python framework to
        set up application, i.e., for REST API, you could select using *flask* to set up application to fake APIs.
        """
        self._parser_args: Dict[str, Any] = {
            "prog": self._prog,
            "usage": self._usage,
            "description": self._description,
            "formatter_class": argparse.RawTextHelpFormatter,
        }

        self._parser = None

        self._command_options: List["CommandOption"] = make_options()
        self._subcommand_info: Optional[SysArg] = None

    @property
    def parser(self) -> argparse.ArgumentParser:
        return self._parser

    @property
    def subcommand(self) -> Optional[SysArg]:
        if self.is_running_subcmd:
            if self._subcommand_info is None:
                self._subcommand_info = SysArg.parse(sys.argv)
            return self._subcommand_info
        else:
            return None

    @property
    def is_running_subcmd(self) -> bool:
        return True in [arg in get_all_subcommands() for arg in sys.argv]

    def parse(self) -> argparse.ArgumentParser:
        """Initial and parse the arguments of current running command line.

        Returns:
            A parser object which is *argparse.ArgumentParser* type.

        """
        if not self.parser:
            self._parser = argparse.ArgumentParser(**self._parser_args)

        for option in self._command_options:
            option.add_option(parser=self.parser)

        return self.parser
