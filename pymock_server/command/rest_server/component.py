from argparse import ArgumentParser

from pymock_server.command._base.component import BaseSubCmdComponent
from pymock_server.command.subcommand import SubCommandLine
from pymock_server.model.command.rest_server.cmd_args import ParserArguments


class SubCmdRestServerComponent(BaseSubCmdComponent):

    def process(self, parser: ArgumentParser, args: ParserArguments) -> None:
        print("⚠️ warn: please operate on this command with one more subcommand line you need.")
        parser.parse_args(args=[SubCommandLine.RestServer.value, "--help"])
