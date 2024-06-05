from typing import Any, Dict, Optional

from ...model.api_config import APIConfig
from ...model.api_config.template._divide import DivideStrategy
from ...model.cmd_args import _BaseSubCmdArgumentsSavingConfig


class SavingConfigComponent:

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
