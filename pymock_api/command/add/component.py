import os
import sys

from ..._utils import YAML
from ...model import APIConfig, generate_empty_config, load_config
from ...model.api_config import MockAPI
from ...model.cmd_args import SubcmdAddArguments
from ...model.enums import ResponseStrategy
from ..component import BaseSubCmdComponent


def _option_cannot_be_empty_assertion(cmd_option: str) -> str:
    return f"Option '{cmd_option}' value cannot be empty."


class SubCmdAddComponent(BaseSubCmdComponent):
    def process(self, args: SubcmdAddArguments) -> None:  # type: ignore[override]
        # TODO: Add logic about using mapping file operation by the file extension.
        assert args.api_config_path, _option_cannot_be_empty_assertion("-o, --output")
        if not args.api_info_is_complete():
            print(f"❌  API info is not enough to add new API.")
            sys.exit(1)
        yaml: YAML = YAML()
        api_config = self._get_api_config(args)
        api_config = self._generate_api_config(api_config, args)
        yaml.write(path=args.api_config_path, config=api_config.serialize())  # type: ignore[arg-type]

    def _get_api_config(self, args: SubcmdAddArguments) -> APIConfig:
        if os.path.exists(args.api_config_path):
            api_config = load_config(args.api_config_path)
            if not api_config:
                api_config = generate_empty_config()
        else:
            api_config = generate_empty_config()
        return api_config

    def _generate_api_config(self, api_config: APIConfig, args: SubcmdAddArguments) -> APIConfig:
        assert api_config.apis is not None
        base = api_config.apis.base
        mocked_api = MockAPI()
        if args.api_path:
            mocked_api.url = args.api_path.replace(base.url, "") if base else args.api_path
        if args.http_method or args.parameters:
            try:
                mocked_api.set_request(method=args.http_method, parameters=args.parameters)  # type: ignore[arg-type]
            except ValueError:
                print("❌  The data format of API parameter is incorrect.")
                sys.exit(1)
        if args.response_strategy is ResponseStrategy.OBJECT:
            mocked_api.set_response(strategy=args.response_strategy, iterable_value=args.response_value)
        else:
            if args.response_value and not isinstance(args.response_value[0], str):
                print("❌  The data type of command line option *--response-value* must be *str*.")
                sys.exit(1)
            mocked_api.set_response(
                strategy=args.response_strategy, value=args.response_value[0] if args.response_value else None  # type: ignore[arg-type]
            )
        api_config.apis.apis[args.api_path] = mocked_api
        return api_config
