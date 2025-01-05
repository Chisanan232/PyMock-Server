from argparse import Namespace

from pymock_server.command.subcommand import SubCommandLine
from pymock_server.model import ParserArguments
from pymock_server.model.subcmd_common import SysArg


class DummyParserArguments(ParserArguments):
    @classmethod
    def deserialize(cls, args: Namespace) -> "DummyParserArguments":
        return DummyParserArguments(subparser_structure=SysArg(subcmd=SubCommandLine.Base))
