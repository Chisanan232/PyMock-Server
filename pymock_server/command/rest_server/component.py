from argparse import ArgumentParser

from pymock_server.command.component import BaseSubCmdComponent
from pymock_server.command.subcommand import SubCommand
from pymock_server.model.cmd_args import ParserArguments


class SubCmdRestServerComponent(BaseSubCmdComponent):

    def process(self, parser: ArgumentParser, args: ParserArguments) -> None:
        print("⚠️ warn: please operate on this command with one more subcommand line you need.")
        parser.parse_args(args=[SubCommand.RestServer, "--help"])
