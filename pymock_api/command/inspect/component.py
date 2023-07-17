from ...model import load_config
from ...model.cmd_args import SubcmdGetArguments
from ..component import BaseSubCmdComponent


class SubCmdGetComponent(BaseSubCmdComponent):
    def process(self, args: SubcmdGetArguments) -> None:  # type: ignore[override]
        current_api_config = load_config(path=args.config_path)
        # TODO: Add implementation about *inspect* feature gets some details of config
