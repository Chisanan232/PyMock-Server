from typing import Any, Dict, Optional

from ..._utils import YAML
from ...model.api_config import APIConfig
from ...model.api_config.template._divide import DivideStrategy
from ...model.cmd_args import _BaseSubCmdArgumentsSavingConfig


class SavingConfigComponent:

    def __init__(self):
        self._file = YAML()

    def serialize_api_config_with_cmd_args(
        self, cmd_args: _BaseSubCmdArgumentsSavingConfig, api_config: APIConfig
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

    def save_api_config(
        self, cmd_args: _BaseSubCmdArgumentsSavingConfig, serialized_api_config: Optional[Dict[str, Any]]
    ) -> None:
        if cmd_args.dry_run:
            self._dry_run_final_process(serialized_api_config)
        else:
            self._final_process(cmd_args, serialized_api_config)

    def _final_process(
        self, cmd_args: _BaseSubCmdArgumentsSavingConfig, serialized_api_config: Optional[Dict[str, Any]]
    ) -> None:
        print("Write the API configuration to file ...")
        self._file.write(path=cmd_args.config_path, config=serialized_api_config, mode="w+")
        print(f"All configuration has been writen in file '{cmd_args.config_path}'.")

    def _dry_run_final_process(self, serialized_api_config: Optional[Dict[str, Any]]) -> None:
        print("The result serialized API configuration:\n")
        print(serialized_api_config)
