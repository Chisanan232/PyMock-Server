from abc import ABCMeta, abstractmethod
from argparse import ArgumentParser
from typing import TypeVar

from pymock_server.model.cmd_args import ParserArguments

ParserArgumentsType = TypeVar("ParserArgumentsType", bound=ParserArguments)


class BaseSubCmdComponent(metaclass=ABCMeta):
    @abstractmethod
    def process(self, parser: ArgumentParser, args: ParserArgumentsType) -> None:
        pass


class NoSubCmdComponent(BaseSubCmdComponent):
    def process(self, parser: ArgumentParser, args: ParserArgumentsType) -> None:
        # FIXME: Should be fix this issue as rest-server
        pass
