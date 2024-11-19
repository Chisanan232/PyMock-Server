import argparse
import sys
from typing import Any, Dict, List, Optional

from pymock_server.command._base.options import CommandOption
from pymock_server.model.subcmd_common import SysArg

from .options import get_all_subcommands, make_options


class MockAPICommandParser:
    """*The parser of PyMock-API command line*

    Handling the command line about options includes what options PyMock-API could use and what values of entry command
    line.
    """

    def __init__(self):
        self._prog = "pymock-api"
        self._usage = "mock" if self.is_running_subcmd else "mock [SUBCOMMAND] [OPTIONS]"
        self._description = """
        A Python tool for mocking APIs by set up an application easily. PyMock-API bases on Python framework to set
        up application, i.e., for REST API, you could select using *flask* to set up application to mock APIs.
        """
        self._parser_args: Dict[str, Any] = {
            "prog": self._prog,
            "usage": self._usage,
            "description": self._description,
        }

        self._parser = None

        self._command_options: List["CommandOption"] = make_options()

    @property
    def parser(self) -> argparse.ArgumentParser:
        return self._parser

    @property
    def subcommand(self) -> Optional[SysArg]:
        return SysArg.parse(sys.argv) if self.is_running_subcmd else None

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
