from argparse import ArgumentParser

from ...model.cmd_args import ParserArguments
from ..component import BaseSubCmdComponent
from ..options import SubCommand


class SubCmdRestServerComponent(BaseSubCmdComponent):

    def process(self, parser: ArgumentParser, args: ParserArguments) -> None:
        print("⚠️ warn: please operate on this command with one more subcommand line you need.")
        parser.parse_args(args=[SubCommand.Rest_Server, "--help"])
