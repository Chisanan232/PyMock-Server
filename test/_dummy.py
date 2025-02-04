from argparse import Namespace

from fake_api_server.command.subcommand import SubCommandLine
from fake_api_server.model import ParserArguments
from fake_api_server.model.subcmd_common import SysArg


class DummyParserArguments(ParserArguments):
    @classmethod
    def deserialize(cls, args: Namespace) -> "DummyParserArguments":
        return DummyParserArguments(subparser_structure=SysArg(subcmd=SubCommandLine.Base))
