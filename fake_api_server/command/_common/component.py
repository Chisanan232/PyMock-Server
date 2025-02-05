import logging
import pathlib
from typing import Any, Dict, Optional

from fake_api_server._utils import YAML
from fake_api_server.model.api_config import FakeAPIConfig
from fake_api_server.model.api_config.template._divide import DivideStrategy
from fake_api_server.model.command.rest_server.cmd_args import (
    _BaseSubCmdArgumentsSavingConfig,
)

logger = logging.getLogger(__name__)


class SavingConfigComponent:

    def __init__(self):
        self._file = YAML()

    def serialize_and_save(self, cmd_args: _BaseSubCmdArgumentsSavingConfig, api_config: FakeAPIConfig) -> None:
        serialized_api_config = self.serialize_api_config_with_cmd_args(cmd_args=cmd_args, api_config=api_config)
        self.save_api_config(cmd_args, serialized_api_config)

    def serialize_api_config_with_cmd_args(
        self, cmd_args: _BaseSubCmdArgumentsSavingConfig, api_config: FakeAPIConfig
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
            self._dry_run_final_process(cmd_args, serialized_api_config)
        else:
            self._final_process(cmd_args, serialized_api_config)

    def _final_process(
        self, cmd_args: _BaseSubCmdArgumentsSavingConfig, serialized_api_config: Optional[Dict[str, Any]]
    ) -> None:
        logger.info("Write the API configuration to file ...")
        self._file.write(path=cmd_args.config_path, config=serialized_api_config, mode="w+")
        logger.info(f"All configuration has been writen in file '{cmd_args.config_path}'.")

    def _dry_run_final_process(
        self, cmd_args: _BaseSubCmdArgumentsSavingConfig, serialized_api_config: Optional[Dict[str, Any]]
    ) -> None:
        if len(str(serialized_api_config)) > 1000:
            dry_run_file_path = str(pathlib.Path(cmd_args.base_file_path, "dry-run_result.yaml"))
            logger.info(
                f"The serialized API configuration content is too much, the result will be saves at *{dry_run_file_path}*"
            )
            self._file.write(path=dry_run_file_path, config=serialized_api_config, mode="w+")
        else:
            logger.info("The result serialized API configuration:\n")
            logger.info(serialized_api_config)
