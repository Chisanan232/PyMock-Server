import sys

from ...model import load_config
from ...model.cmd_args import SubcmdGetArguments
from ..component import BaseSubCmdComponent


class SubCmdGetComponent(BaseSubCmdComponent):
    def process(self, args: SubcmdGetArguments) -> None:  # type: ignore[override]
        current_api_config = load_config(path=args.config_path)
        if current_api_config is None:
            print("❌  Empty content in configuration file.")
            sys.exit(1)
        apis_info = current_api_config.apis
        if apis_info is None:
            print("❌  Cannot find any API setting to mock.")
            sys.exit(1)
        specific_api_info = apis_info.get_api_config_by_url(url=args.api_path, base=apis_info.base)
        if specific_api_info:
            print("🍻  Find the API info which satisfy the conditions.")
            print("+--------------- API info ---------------+")
            print(f"+ Path:  {specific_api_info.url}")
            print(f"+ HTTP:")
            http_info = specific_api_info.http
            print("+   Request:")
            if http_info and http_info.request:
                print(f"+     HTTP method:  {http_info.request.method}")
                print("+       Parameters:")
                for param in http_info.request.parameters:
                    print(f"+         name:  {param.name}")
                    print(f"+           required:  {param.required}")
                    print(f"+           default value:  {param.default}")
                    print(f"+           data type:  {param.value_type}")
                    print(f"+           value format:  {param.value_format}")
            else:
                print("+     Miss settings.")
            print("+     Response:")
            if http_info and http_info.response:
                print(f"+       Values:  {http_info.response.value}")
            else:
                print("+     Miss settings.")
            sys.exit(0)
        else:
            print("🙅‍♂️  Cannot find the API info with the conditions.")
            sys.exit(1)
        # TODO: Add implementation about *inspect* feature gets some details of config