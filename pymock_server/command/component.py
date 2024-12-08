from argparse import ArgumentParser

from ._base.component import BaseSubCmdComponent, ParserArgumentsType


class NoSubCmdComponent(BaseSubCmdComponent):
    def process(self, parser: ArgumentParser, args: ParserArgumentsType) -> None:
        # FIXME: Should be fix this issue as rest-server
        pass
