import os
import re
from argparse import ArgumentParser

from fake_api_server._utils import import_web_lib
from fake_api_server.command._base.component import BaseSubCmdComponent
from fake_api_server.exceptions import InvalidAppType, NoValidWebLibrary
from fake_api_server.model import SubcmdRunArguments
from fake_api_server.server import BaseSGIServer, setup_asgi, setup_wsgi


def _option_cannot_be_empty_assertion(cmd_option: str) -> str:
    return f"Option '{cmd_option}' value cannot be empty."


class SubCmdRunComponent(BaseSubCmdComponent):
    def __init__(self):
        super().__init__()
        self._server_gateway: BaseSGIServer = None

    def process(self, parser: ArgumentParser, args: SubcmdRunArguments) -> None:  # type: ignore[override]
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
