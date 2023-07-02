import copy
import json
import os
import pathlib
import re
import sys
from argparse import ArgumentParser, Namespace
from typing import Any, Callable, List, Optional, Tuple, Type, cast
from urllib3 import PoolManager, BaseHTTPResponse

from ._utils import YAML, import_web_lib
from .cmd import MockAPICommandParser, SubCommand
from .exceptions import InvalidAppType, NoValidWebLibrary
from .model import (
    APIConfig,
    ParserArguments,
    SubcmdCheckArguments,
    SubcmdConfigArguments,
    SubcmdRunArguments,
    SubcmdInspectArguments,
    deserialize_args,
    load_config,
)
from .model._sample import Sample_Config_Value
from .server import BaseSGIServer, setup_asgi, setup_wsgi

_COMMAND_CHAIN: List[Type["CommandProcessor"]] = []


def dispatch_command_processor() -> "CommandProcessor":
    cmd_chain = make_command_chain()
    assert len(cmd_chain) > 0, "It's impossible that command line processors list is empty."
    return cmd_chain[0].distribute()


def run_command_chain(args: ParserArguments) -> None:
    cmd_chain = make_command_chain()
    assert len(cmd_chain) > 0, "It's impossible that command line processors list is empty."
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

        # # Check whether it has anything in configuration or not
        SubCmdCheck._setting_should_not_be_none(
            config_key="",
            config_value=api_config,
            err_msg="Configuration is empty.",
        )

        # # Check the section *mocked_apis* (first layer) of configuration
        assert api_config is not None
        SubCmdCheck._setting_should_not_be_none(
            config_key="mocked_apis",
            config_value=api_config.apis,
        )

        # NOTE: It's the normal behavior of code implementation. It must have something of property *MockAPIs.apis*
        # if it has anything within key *mocked_apis*.
        assert api_config.apis and api_config.apis.apis

        # # Check each API content at first layer is *mocked_apis* of configuration
        for one_api_name, one_api_config in api_config.apis.apis.items():
            # # Check the section *mocked_apis.<API name>* (second layer) of configuration
            SubCmdCheck._setting_should_not_be_none(
                config_key=f"mocked_apis.{one_api_name}",
                config_value=one_api_config,
            )

            # # Check the section *mocked_apis.<API name>.<property>* (third layer) of configuration (not include the
            # # layer about API name, should be the first layer under API name)
            assert one_api_config
            SubCmdCheck._setting_should_not_be_none(
                config_key=f"mocked_apis.{one_api_name}.url",
                config_value=one_api_config.url,
            )
            SubCmdCheck._setting_should_not_be_none(
                config_key=f"mocked_apis.{one_api_name}.http",
                config_value=one_api_config.http,
            )

            # # Check the section *mocked_apis.<API name>.http.<property>* (forth layer) of configuration
            assert one_api_config.http
            SubCmdCheck._setting_should_not_be_none(
                config_key=f"mocked_apis.{one_api_name}.http.request",
                config_value=one_api_config.http.request,
            )

            assert one_api_config.http.request
            SubCmdCheck._setting_should_not_be_none(
                config_key=f"mocked_apis.{one_api_name}.http.request.method",
                config_value=one_api_config.http.request.method,
            )
            SubCmdCheck._setting_should_be_valid(
                config_key=f"mocked_apis.{one_api_name}.http.request.method",
                config_value=one_api_config.http.request.method.upper(),
                criteria=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTION"],
            )

            SubCmdCheck._setting_should_not_be_none(
                config_key=f"mocked_apis.{one_api_name}.http.response",
                config_value=one_api_config.http.response,
            )

            assert one_api_config.http.response
            SubCmdCheck._setting_should_not_be_none(
                config_key=f"mocked_apis.{one_api_name}.http.response.value",
                config_value=one_api_config.http.response.value,
                valid_callback=self._chk_response_value_validity,
            )

        print("Configuration is valid.")
        sys.exit(0)

    def _chk_response_value_validity(self, config_key: str, config_value: Any) -> None:
        try:
            json.loads(config_value)
        except:
            if re.search(r"\w{1,32}\.\w{1,8}", config_value):
                if not pathlib.Path(config_value).exists():
                    print("The file which is the response content doesn't exist.")
                    sys.exit(1)
            # else:
            #     print("Data content format is incorrect")
            #     sys.exit(1)

    @staticmethod
    def _setting_should_not_be_none(
        config_key: str, config_value: Any, valid_callback: Optional[Callable] = None, err_msg: Optional[str] = None
    ) -> None:
        if config_value is None:
            print(err_msg if err_msg else f"Configuration *{config_key}* content cannot be empty.")
            sys.exit(1)
        else:
            if valid_callback:
                valid_callback(config_key, config_value)

    @staticmethod
    def _setting_should_be_valid(
        config_key: str, config_value: Any, criteria: list, valid_callback: Optional[Callable] = None
    ) -> None:
        if not isinstance(criteria, list):
            raise TypeError("The argument *criteria* only accept 'list' type value.")

        if config_value not in criteria:
            is_valid = False
        else:
            is_valid = True

        if not is_valid:
            print(f"Configuration *{config_key}* value is invalid.")
            sys.exit(1)
        else:
            if valid_callback:
                valid_callback(config_key, config_value, criteria)


class SubCmdInspect(BaseCommandProcessor):
    responsible_subcommand = SubCommand.Inspect

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> SubcmdInspectArguments:
        return deserialize_args.subcmd_inspect(self._parse_cmd_arguments(parser, cmd_args))

    def _run(self, args: SubcmdInspectArguments) -> None:
        current_api_config: APIConfig = load_config(path=args.config_path)
        base_info = current_api_config.apis.base
        mocked_apis_info = current_api_config.apis.apis
        if base_info:
            mocked_apis_path = list(map(lambda p: f"{base_info.url}{p.url}", mocked_apis_info.values()))
        else:
            mocked_apis_path = list(map(lambda p: p.url, mocked_apis_info.values()))

        pm: PoolManager = PoolManager()
        resp: BaseHTTPResponse = pm.request(method="GET", url=args.swagger_doc_url)
        swagger_api_doc: dict = resp.json()
        for swagger_api_path, swagger_api_props in swagger_api_doc["paths"].items():
            # Check API path
            if swagger_api_path not in mocked_apis_path:
                print(f"⚠️  Miss API. Path: {swagger_api_path}")
                sys.exit(1)

            for swagger_one_api_method, swagger_one_api_props in cast(dict, swagger_api_props).items():
                api_http_config = current_api_config.apis.get_api_config_by_url(swagger_api_path).http

                # Check API HTTP method
                if str(swagger_one_api_method).upper() != api_http_config.request.method.upper():
                    print(f"⚠️  Miss the API with HTTP method {swagger_one_api_method}")
                    sys.exit(1)

                # Check API parameters
                api_params = swagger_one_api_props["parameters"]
                param_names = list(map(lambda p: p.name, api_http_config.request.parameters))
                has_params: bool = False
                for one_api_params in api_params:
                    if one_api_params["name"] in param_names:
                        has_params = True
                        break
                if not has_params:
                    print(f"⚠️  Miss the API parameter {param_names}")
                    sys.exit(1)

                # Check API response
                api_resp = swagger_one_api_props["responses"]["200"]
        print(f"🍻  All mock APIs are already be updated with Swagger API document {args.swagger_doc_url}.")
        sys.exit(0)
