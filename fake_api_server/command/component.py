from argparse import ArgumentParser

from ._base.component import BaseSubCmdComponent, ParserArgumentsType


class NoSubCmdComponent(BaseSubCmdComponent):
    def process(self, parser: ArgumentParser, args: ParserArgumentsType) -> None:
        print("⚠️ warn: please operate on this command with one more options or subcommand line you need.")
        parser.parse_args(args=["--help"])
