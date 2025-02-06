import logging
import os
import sys
from argparse import ArgumentParser

from fake_api_server.command._base.component import BaseSubCmdComponent
from fake_api_server.command._common.component import SavingConfigComponent
from fake_api_server.model import (
    FakeAPIConfig,
    MockAPI,
    generate_empty_config,
    load_config,
)
from fake_api_server.model.api_config.apis.response_strategy import ResponseStrategy
from fake_api_server.model.command.rest_server.cmd_args import SubcmdAddArguments

logger = logging.getLogger(__name__)


def _option_cannot_be_empty_assertion(cmd_option: str) -> str:
    return f"Option '{cmd_option}' value cannot be empty."


class SubCmdAddComponent(BaseSubCmdComponent):
    def __init__(self):
        self._saving_config_component = SavingConfigComponent()

    def process(self, parser: ArgumentParser, args: SubcmdAddArguments) -> None:  # type: ignore[override]
        # TODO: Add logic about using mapping file operation by the file extension.
        assert args.config_path, _option_cannot_be_empty_assertion("-o, --output")
        if not args.api_info_is_complete():
            logger.error("❌  API info is not enough to add new API.")
            sys.exit(1)
        api_config = self._get_api_config(args)
        api_config = self._generate_api_config(api_config, args)
        self._saving_config_component.serialize_and_save(cmd_args=args, api_config=api_config)

    def _get_api_config(self, args: SubcmdAddArguments) -> FakeAPIConfig:
        if os.path.exists(args.config_path):
            api_config = load_config(args.config_path)
            if not api_config:
                api_config = generate_empty_config()
        else:
            api_config = generate_empty_config()
        return api_config

    def _generate_api_config(self, api_config: FakeAPIConfig, args: SubcmdAddArguments) -> FakeAPIConfig:
        assert api_config.apis is not None
        # Set *base*
        if args.base_url:
            assert api_config.apis.base, "Section *base* must not be empty."
            api_config.apis.base.url = args.base_url
        base = api_config.apis.base

        mocked_api = MockAPI()
        # Set *<mock_api>.tag*
        if args.tag:
            mocked_api.tag = args.tag
        # Set *<mock_api>.url*
        if args.api_path:
            mocked_api.url = args.api_path.replace(base.url, "") if base else args.api_path
        # Set *<mock_api>.http.request*
        if args.http_method or args.parameters:
            try:
                mocked_api.set_request(method=args.http_method, parameters=args.parameters)  # type: ignore[arg-type]
            except ValueError:
                logger.error("❌  The data format of API parameter is incorrect.")
                sys.exit(1)
        # Set *<mock_api>.http.response*
        if args.response_strategy is ResponseStrategy.OBJECT:
            mocked_api.set_response(strategy=args.response_strategy, iterable_value=args.response_value)
        else:
            if args.response_value and not isinstance(args.response_value[0], str):
                logger.error("❌  The data type of command line option *--response-value* must be *str*.")
                sys.exit(1)
            mocked_api.set_response(
                strategy=args.response_strategy, value=args.response_value[0] if args.response_value else None  # type: ignore[arg-type]
            )
        # Set up *<mock_api>* in configuration
        api_config.apis.apis[self._generate_api_key(args)] = mocked_api

        return api_config

    def _generate_api_key(self, args: SubcmdAddArguments) -> str:
        return "_".join([args.http_method.lower(), args.api_path.replace(args.base_url, "")[1:].replace("/", "_")])
