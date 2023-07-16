from ...model import load_config
from ...model.cmd_args import SubcmdInspectArguments
from ..component import BaseSubCmdComponent


class SubCmdInspectComponent(BaseSubCmdComponent):
    def process(self, args: SubcmdInspectArguments) -> None:  # type: ignore[override]
        current_api_config = load_config(path=args.config_path)
        # TODO: Add implementation about *inspect* feature gets some details of config
