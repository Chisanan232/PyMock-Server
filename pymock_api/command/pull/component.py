from pathlib import Path
from typing import Union

from ..._utils import JSON
from ..._utils.api_client import URLLibHTTPClient
from ...model import OpenAPIDocumentConfig, deserialize_openapi_doc_config
from ...model.cmd_args import SubcmdPullArguments
from .._common.component import SavingConfigComponent
from ..component import BaseSubCmdComponent


class SubCmdPullComponent(BaseSubCmdComponent):
    def __init__(self):
        self._api_client = URLLibHTTPClient()
        # self._file = YAML()

        self._saving_config_component = SavingConfigComponent()

    def process(self, args: SubcmdPullArguments) -> None:  # type: ignore[override]
        openapi_doc_url: str = ""
        openapi_doc_config_file: str = ""
        source_info_log: str = ""
        if args.source:
            http_proto = "https" if args.request_with_https else "http"
            openapi_doc_url = f"{http_proto}://{args.source}"
            source_info_log = f"host '{openapi_doc_url}'"
        if args.source_file:
            openapi_doc_config_file = args.source_file
            source_info_log = (
                f"configuration file '{openapi_doc_config_file}'" if not source_info_log else source_info_log
            )
        print(f"Try to get OpenAPI API (aka Swagger API before) documentation content from {source_info_log}.")
        openapi_doc_config = self._get_openapi_doc_config(url=openapi_doc_url, config_file=openapi_doc_config_file)
        api_config = openapi_doc_config.to_api_config(base_url=args.base_url)
        serialized_api_config = self._saving_config_component.serialize_api_config_with_cmd_args(
            cmd_args=args, api_config=api_config
        )
        self._saving_config_component.save_api_config(args, serialized_api_config)

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
