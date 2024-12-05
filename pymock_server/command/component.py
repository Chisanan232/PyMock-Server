from abc import ABCMeta, abstractmethod
from argparse import ArgumentParser
from typing import TypeVar

from ..model.cmd_args import ParserArguments

ParserArgumentsType = TypeVar("ParserArgumentsType", bound=ParserArguments)


class BaseSubCmdComponent(metaclass=ABCMeta):
    @abstractmethod
    def process(self, parser: ArgumentParser, args: ParserArgumentsType) -> None:
        pass


class NoSubCmdComponent(BaseSubCmdComponent):
    def process(self, parser: ArgumentParser, args: ParserArgumentsType) -> None:
        pass
