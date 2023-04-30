import copy
import json
import os
import pathlib
import re
import sys
from argparse import ArgumentParser, Namespace
from typing import List, Optional, Tuple, Type

from ._utils import YAML, import_web_lib
from .cmd import MockAPICommandParser, SubCommand
from .exceptions import InvalidAppType, NoValidWebLibrary
from .model import (
    APIConfig,
    ParserArguments,
    SubcmdCheckArguments,
    SubcmdConfigArguments,
    SubcmdRunArguments,
    deserialize_args,
    load_config,
)
from .model._sample import Sample_Config_Value
from .server import BaseSGIServer, setup_asgi, setup_wsgi

_COMMAND_CHAIN: List[Type["CommandProcessor"]] = []


def dispatch_command_processor() -> "CommandProcessor":
    cmd_chain = make_command_chain()
    return cmd_chain[0].distribute()


def run_command_chain(args: ParserArguments) -> None:
    cmd_chain = make_command_chain()
    cmd_chain[0].process(args)


def make_command_chain() -> List["CommandProcessor"]:
    existed_subcmd: List[Optional[str]] = []
    mock_api_cmd: List["CommandProcessor"] = []
    for cmd_cls in _COMMAND_CHAIN:
        cmd = cmd_cls()
        if cmd.responsible_subcommand in existed_subcmd:
            raise ValueError(f"The subcommand *{cmd.responsible_subcommand}* has been used. Please use other naming.")
        existed_subcmd.append(getattr(cmd, "responsible_subcommand"))
        mock_api_cmd.append(cmd.copy())
    return mock_api_cmd


def _option_cannot_be_empty_assertion(cmd_option: str) -> str:
    return f"Option '{cmd_option}' value cannot be empty."


class MetaCommand(type):
    """*The metaclass for options of PyMock-API command*

    content ...
    """

    def __new__(cls, name: str, bases: Tuple[type], attrs: dict):
        super_new = super().__new__
        parent = [b for b in bases if isinstance(b, MetaCommand)]
        if not parent:
            return super_new(cls, name, bases, attrs)
        new_class = super_new(cls, name, bases, attrs)
        _COMMAND_CHAIN.append(new_class)  # type: ignore
        return new_class


class CommandProcessor:
    responsible_subcommand: Optional[str] = None

    def __init__(self):
        self.mock_api_parser = MockAPICommandParser()
        self._current_index = 0

    @property
    def _next(self) -> "CommandProcessor":
        if self._current_index == len(_COMMAND_CHAIN):
            raise StopIteration
        cmd = _COMMAND_CHAIN[self._current_index]
        self._current_index += 1
        return cmd()

    def distribute(self, args: Optional[ParserArguments] = None, cmd_index: int = 0) -> "CommandProcessor":
        if self._is_responsible(subcmd=self.mock_api_parser.subcommand, args=args):
            return self
        else:
            self._current_index = cmd_index
            return self._next.distribute(args=args, cmd_index=self._current_index)

    def process(self, args: ParserArguments, cmd_index: int = 0) -> None:
        self.distribute(args=args, cmd_index=cmd_index)._run(args)

    def parse(
        self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None, cmd_index: int = 0
    ) -> ParserArguments:
        return self.distribute(cmd_index=cmd_index)._parse_process(parser=parser, cmd_args=cmd_args)

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> ParserArguments:
        raise NotImplementedError

    def copy(self) -> "CommandProcessor":
        return copy.copy(self)

    def _is_responsible(self, subcmd: Optional[str] = None, args: Optional[ParserArguments] = None) -> bool:
        if args:
            return args.subparser_name == self.responsible_subcommand
        return subcmd == self.responsible_subcommand

    def _run(self, args: ParserArguments) -> None:
        raise NotImplementedError

    def _parse_cmd_arguments(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> Namespace:
        return parser.parse_args(cmd_args)


BaseCommandProcessor: type = MetaCommand("BaseCommandProcessor", (CommandProcessor,), {})


class NoSubCmd(BaseCommandProcessor):
    responsible_subcommand: Optional[str] = None

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> ParserArguments:
        return self._parse_cmd_arguments(parser, cmd_args)

    def _run(self, args: ParserArguments) -> None:
        pass


class SubCmdRun(BaseCommandProcessor):
    responsible_subcommand = SubCommand.Run

    def __init__(self):
        super().__init__()
        self._server_gateway: BaseSGIServer = None

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> SubcmdRunArguments:
        return deserialize_args.subcmd_run(self._parse_cmd_arguments(parser, cmd_args))

    def _run(self, args: SubcmdRunArguments) -> None:
        self._process_option(args)
        self._server_gateway.run(args)

    def _process_option(self, parser_options: SubcmdRunArguments) -> None:
        # Note: It's possible that it should separate the functions to be multiple objects to implement and manage the
        # behaviors of command line with different options.
        # Handle *config*
        if parser_options.config:
            os.environ["MockAPI_Config"] = parser_options.config

        # Handle *app-type*
        assert parser_options.app_type, _option_cannot_be_empty_assertion("--app-type")
        self._initial_server_gateway(lib=parser_options.app_type)

    def _initial_server_gateway(self, lib: str) -> None:
        if re.search(r"auto", lib, re.IGNORECASE):
            web_lib = import_web_lib.auto_ready()
            if not web_lib:
                raise NoValidWebLibrary
            self._initial_server_gateway(lib=web_lib)
        elif re.search(r"flask", lib, re.IGNORECASE):
            self._server_gateway = setup_wsgi()
        elif re.search(r"fastapi", lib, re.IGNORECASE):
            self._server_gateway = setup_asgi()
        else:
            raise InvalidAppType


class SubCmdConfig(BaseCommandProcessor):
    responsible_subcommand = SubCommand.Config

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> SubcmdConfigArguments:
        return deserialize_args.subcmd_config(self._parse_cmd_arguments(parser, cmd_args))

    def _run(self, args: SubcmdConfigArguments) -> None:
        yaml: YAML = YAML()
        sample_data: str = yaml.serialize(config=Sample_Config_Value)
        if args.print_sample:
            print(f"It will write below content into file {args.sample_output_path}:")
            print(f"{sample_data}")
        if args.generate_sample:
            assert args.sample_output_path, _option_cannot_be_empty_assertion("-o, --output")
            yaml.write(path=args.sample_output_path, config=sample_data)


class SubCmdCheck(BaseCommandProcessor):
    responsible_subcommand = SubCommand.Check

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> SubcmdCheckArguments:
        return deserialize_args.subcmd_check(self._parse_cmd_arguments(parser, cmd_args))

    def _run(self, args: SubcmdCheckArguments) -> None:
        api_config: Optional[APIConfig] = load_config(path=args.config_path)
        if api_config is None:
            print("Configuration is empty.")
            sys.exit(1)

        if api_config.apis:
            # NOTE: It's the normal behavior of code implementation. It must have something of property *MockAPIs.apis*
            # if it has anything within key *mocked_apis*.
            assert api_config.apis.apis

            for one_api_name, one_api_config in api_config.apis.apis.items():
                if one_api_config is None:
                    print(f"Configuration *mocked_apis.{one_api_name}* content is empty.")
                    sys.exit(1)

                if one_api_config.url is None:
                    print(f"Configuration *mocked_apis.{one_api_name}.url* content is empty.")
                    sys.exit(1)

                if one_api_config.http is None:
                    print(f"Configuration *mocked_apis.{one_api_name}.http* content is empty.")
                    sys.exit(1)

                if one_api_config.http.request is None:
                    print(f"Configuration *mocked_apis.{one_api_name}.http.request* content is empty.")
                    sys.exit(1)

                if one_api_config.http.request.method is None:
                    print(f"Configuration *mocked_apis.{one_api_name}.http.request.method* content is empty.")
                    sys.exit(1)

                if one_api_config.http.request.method.upper() not in ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTION"]:
                    print(f"Configuration *mocked_apis.{one_api_name}.http.request.method* content is empty.")
                    sys.exit(1)

                if one_api_config.http.response is None:
                    print(f"Configuration *mocked_apis.{one_api_name}.http.response* content is empty.")
                    sys.exit(1)

                if one_api_config.http.response.value is None:
                    print(f"Configuration *mocked_apis.{one_api_name}.http.response.value* content is empty.")
                    sys.exit(1)

                if one_api_config.http.response.value:
                    try:
                        json.loads(one_api_config.http.response.value)
                    except:
                        is_file_name_format = re.search(r"\w{1,32}\.\w{1,8}", one_api_config.http.response.value)
                        if is_file_name_format:
                            if not pathlib.Path(one_api_config.http.response.value).exists():
                                print("File doesn't exist")
                                sys.exit(1)
                        # else:
                        #     print("Data content format is incorrect")
                        #     sys.exit(1)
        else:
            print("Configuration *mocked_apis* content is empty.")
            sys.exit(1)

        print("Configuration is valid.")
        sys.exit(0)
