from pathlib import Path
from typing import Any, Dict, Optional, Union

from ..._utils import JSON, YAML
from ..._utils.api_client import URLLibHTTPClient
from ...model import OpenAPIDocumentConfig, deserialize_openapi_doc_config
from ...model.api_config import APIConfig, DivideStrategy
from ...model.cmd_args import SubcmdPullArguments
from ..component import BaseSubCmdComponent


class SubCmdPullComponent(BaseSubCmdComponent):
    def __init__(self):
        self._api_client = URLLibHTTPClient()
        self._file = YAML()

    def process(self, args: SubcmdPullArguments) -> None:  # type: ignore[override]
        http_proto = "https" if args.request_with_https else "http"
        openapi_doc_url = f"{http_proto}://{args.source}"
        print(f"Try to get OpenAPI API (aka Swagger API before) documentation content at '{openapi_doc_url}'.")
        openapi_doc_config = self._get_openapi_doc_config(url=openapi_doc_url)
        api_config = openapi_doc_config.to_api_config(base_url=args.base_url)
        serialized_api_config = self._serialize_api_config_with_cmd_args(cmd_args=args, api_config=api_config)
        if args.dry_run:
            self._dry_run_final_process(serialized_api_config)
        else:
            self._final_process(args, serialized_api_config)

    def _get_openapi_doc_config(self, url: str = "", config_file: Union[str, Path] = "") -> OpenAPIDocumentConfig:
        openapi_doc_config: dict = {}
        if url:
            openapi_doc_config = self._api_client.request(method="GET", url=url)
        if config_file and not openapi_doc_config:
            openapi_doc_config = JSON().read(path=config_file if isinstance(config_file, str) else str(config_file))
        if not openapi_doc_config:
            raise ValueError(
                "It must has host URL or configuration file path to get the OpenAPI documentation details."
            )
        return deserialize_openapi_doc_config(data=openapi_doc_config)

    def _serialize_api_config_with_cmd_args(
        self, cmd_args: SubcmdPullArguments, api_config: APIConfig
    ) -> Optional[Dict[str, Any]]:
        api_config.is_pull = True

        # section *template*
        api_config.set_template_in_config = cmd_args.include_template_config
        api_config.base_file_path = cmd_args.base_file_path

        # feature about dividing configuration
        api_config.dry_run = cmd_args.dry_run
        api_config.divide_strategy = DivideStrategy(
            divide_api=cmd_args.divide_api,
            divide_http=cmd_args.divide_http,
            divide_http_request=cmd_args.divide_http_request,
            divide_http_response=cmd_args.divide_http_response,
        )

        return api_config.serialize()

    def _final_process(self, cmd_args: SubcmdPullArguments, serialized_api_config: Optional[Dict[str, Any]]) -> None:
        print("Write the API configuration to file ...")
        self._file.write(path=cmd_args.config_path, config=serialized_api_config, mode="w+")
        print(f"All configuration has been writen in file '{cmd_args.config_path}'.")

    def _dry_run_final_process(self, serialized_api_config: Optional[Dict[str, Any]]) -> None:
        print("The result serialized API configuration:\n")
        print(serialized_api_config)
