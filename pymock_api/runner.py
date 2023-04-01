import os
import re
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List, Optional, Union

try:
    import pymock_api.cmd
    from pymock_api._utils.file_opt import YAML
    from pymock_api.model import (
        ParserArguments,
        SubcmdConfigArguments,
        SubcmdRunArguments,
        deserialize_args,
    )
    from pymock_api.model._sample import Sample_Config_Value
    from pymock_api.server import BaseSGIServer, setup_asgi, setup_wsgi
except (ImportError, ModuleNotFoundError):
    runner_dir = os.path.dirname(os.path.abspath(__file__))
    path = str(Path(runner_dir).parent.absolute())
    sys.path.append(path)
    import pymock_api.cmd
    from pymock_api._utils.file_opt import YAML
    from pymock_api.model import (
        ParserArguments,
        SubcmdConfigArguments,
        SubcmdRunArguments,
        deserialize_args,
    )
    from pymock_api.model._sample import Sample_Config_Value
    from pymock_api.server import BaseSGIServer, setup_asgi, setup_wsgi


class CommandRunner:
    def __init__(self):
        self.mock_api_parser = pymock_api.cmd.MockAPICommandParser()
        self.cmd_parser: ArgumentParser = self.mock_api_parser.parse()
        self._server_gateway: BaseSGIServer = None

    # TODO: It may use responsibility chain to design and implement command line features
    def run(self, args: ParserArguments) -> None:
        pass

    def run_app(self, args: SubcmdRunArguments) -> None:
        self._process_option(args)
        self._server_gateway.run(args)

    def run_config(self, args: SubcmdConfigArguments) -> None:
        yaml: YAML = None
        sample_data: str = None
        if args.print_sample or args.generate_sample:
            yaml = YAML()
            sample_data = yaml.serialize(config=Sample_Config_Value)
        if args.print_sample:
            print(f"It will write below content into file {args.sample_output_path}:")
            print(f"{sample_data}")
        if args.generate_sample:
            yaml.write(path=args.sample_output_path, config=sample_data)

    def parse(self, cmd_args: Optional[List[str]] = None) -> Union[SubcmdRunArguments, SubcmdConfigArguments]:
        if self.mock_api_parser.subcommand == pymock_api.cmd.SubCommand.Run:
            return self.parse_subcmd_run(cmd_args)
        elif self.mock_api_parser.subcommand == pymock_api.cmd.SubCommand.Config:
            return self.parse_subcmd_config(cmd_args)
        else:
            return self._parse_cmd_arguments(cmd_args)

    def parse_subcmd_run(self, cmd_args: Optional[List[str]] = None) -> SubcmdRunArguments:
        return deserialize_args.subcmd_run(self._parse_cmd_arguments(cmd_args))

    def parse_subcmd_config(self, cmd_args: Optional[List[str]] = None) -> SubcmdConfigArguments:
        return deserialize_args.subcmd_config(self._parse_cmd_arguments(cmd_args))

    def _parse_cmd_arguments(self, cmd_args: Optional[List[str]] = None) -> Namespace:
        return self.cmd_parser.parse_args(cmd_args)

    def _process_option(self, parser_options: SubcmdRunArguments) -> None:
        # Note: It's possible that it should separate the functions to be multiple objects to implement and manage the
        # behaviors of command line with different options.
        # Handle *config*
        os.environ["MockAPI_Config"] = parser_options.config

        # Handle *app-type*
        if re.search(r"flask", parser_options.app_type, re.IGNORECASE):
            self._server_gateway = setup_wsgi()
        elif re.search(r"fastapi", parser_options.app_type, re.IGNORECASE):
            self._server_gateway = setup_asgi()
        else:
            raise ValueError("Invalid value at argument *app-type*. It only supports 'flask' or 'fastapi' currently.")


def run() -> None:
    cmd_runner = CommandRunner()
    arguments = cmd_runner.parse()
    if arguments.subparser_name == pymock_api.cmd.SubCommand.Run:
        cmd_runner.run_app(arguments)
    elif arguments.subparser_name == pymock_api.cmd.SubCommand.Config:
        cmd_runner.run_config(arguments)
    else:
        cmd_runner.run(arguments)


if __name__ == "__main__":

    run()
