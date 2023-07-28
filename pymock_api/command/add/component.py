import os
import sys

from ..._utils import YAML
from ...model import generate_empty_config, load_config
from ...model._sample import Sample_Config_Value
from ...model.api_config import APIConfig, MockAPI
from ...model.cmd_args import SubcmdAddArguments
from ..component import BaseSubCmdComponent


def _option_cannot_be_empty_assertion(cmd_option: str) -> str:
    return f"Option '{cmd_option}' value cannot be empty."


class SubCmdAddComponent(BaseSubCmdComponent):
    def process(self, args: SubcmdAddArguments) -> None:  # type: ignore[override]
        yaml: YAML = YAML()
        sample_data: str = yaml.serialize(config=Sample_Config_Value)
        if args.print_sample:
            print(f"It will write below content into file {args.sample_output_path}:")
            print(f"{sample_data}")
        if args.generate_sample:
            assert args.sample_output_path, _option_cannot_be_empty_assertion("-o, --output")
            yaml.write(path=args.sample_output_path, config=sample_data)

        if args.api_config_path:
            if not args.api_info_is_complete():
                print(f"❌  API info is not enough to add new API.")
                sys.exit(1)
            if os.path.exists(args.api_config_path):
                api_config = load_config(args.api_config_path)
                if not api_config:
                    api_config = generate_empty_config()
            else:
                api_config = generate_empty_config()

            api_config = self._generate_api_config(api_config, args)
            yaml.write(path=args.api_config_path, config=api_config.serialize())  # type: ignore[arg-type]

    def _generate_api_config(self, api_config: APIConfig, args: SubcmdAddArguments) -> APIConfig:
        assert api_config.apis is not None
        base = api_config.apis.base
        mocked_api = MockAPI()
        if args.api_path:
            mocked_api.url = args.api_path.replace(base.url, "") if base else args.api_path
        if args.http_method or args.parameters:
            try:
                mocked_api.set_request(method=args.http_method, parameters=args.parameters)
            except ValueError:
                print("❌  The data format of API parameter is incorrect.")
                sys.exit(1)
        if args.response:
            mocked_api.set_response(value=args.response)
        api_config.apis.apis[args.api_path] = mocked_api
        return api_config
