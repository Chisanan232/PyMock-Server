from ..._utils import YAML
from ...model._sample import Sample_Config_Value
from ...model.cmd_args import SubcmdConfigArguments
from ..component import BaseSubCmdComponent


def _option_cannot_be_empty_assertion(cmd_option: str) -> str:
    return f"Option '{cmd_option}' value cannot be empty."


class SubCmdConfigComponent(BaseSubCmdComponent):
    def process(self, args: SubcmdConfigArguments) -> None:  # type: ignore[override]
        yaml: YAML = YAML()
        sample_data: str = yaml.serialize(config=Sample_Config_Value)
        if args.print_sample:
            print(f"It will write below content into file {args.sample_output_path}:")
            print(f"{sample_data}")
        if args.generate_sample:
            assert args.sample_output_path, _option_cannot_be_empty_assertion("-o, --output")
            yaml.write(path=args.sample_output_path, config=sample_data)
