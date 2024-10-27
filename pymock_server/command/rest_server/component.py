from ...model.cmd_args import ParserArguments
from ..component import BaseSubCmdComponent


class SubCmdRestServerComponent(BaseSubCmdComponent):

    def process(self, args: ParserArguments) -> None:
        # FIXME: Let this proces just print the help info of how to use subcommand line *rest-server*
        print("Do nothing, please use anyone of subcommand line to do you want to do.")
