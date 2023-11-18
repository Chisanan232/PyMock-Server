from ..._utils import YAML
from ..._utils.api_client import URLLibHTTPClient
from ...model import SwaggerConfig, deserialize_swagger_api_config
from ...model.api_config import _DivideStrategy
from ...model.cmd_args import SubcmdPullArguments
from ..component import BaseSubCmdComponent


class SubCmdPullComponent(BaseSubCmdComponent):
    def __init__(self):
        self._api_client = URLLibHTTPClient()
        self._file = YAML()

    def process(self, args: SubcmdPullArguments) -> None:  # type: ignore[override]
        print(f"Try to get Swagger API documentation content at 'http://{args.source}/'.")
        # TODO: Have a command line option to control it should use http or https to request
        http_proto = "http"
        swagger_api_doc = self._get_swagger_config(swagger_url=f"{http_proto}://{args.source}/")
        api_config = swagger_api_doc.to_api_config(base_url=args.base_url)
        print("Write the API configuration to file ...")
        api_config.set_template_in_config = args.include_template_config
        # TODO: Add command line option to control this setting *dry_run*
        api_config.dry_run = True
        # TODO: Add command line option to control how to divide the configuration
        api_config.divide_strategy = _DivideStrategy(
            divide_api=False,
            divide_http=False,
            divide_http_request=False,
            divide_http_response=False,
        )
        self._file.write(path=args.config_path, config=api_config.serialize())
        print(f"All configuration has been writen in file '{args.config_path}'.")

    def _get_swagger_config(self, swagger_url: str) -> SwaggerConfig:
        swagger_api_doc: dict = self._api_client.request(method="GET", url=swagger_url)
        return deserialize_swagger_api_config(data=swagger_api_doc)
