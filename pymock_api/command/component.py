from abc import ABCMeta, abstractmethod
from typing import TypeVar

from ..model.cmd_args import ParserArguments

ParserArgumentsType = TypeVar("ParserArgumentsType", bound=ParserArguments)


class BaseSubCmdComponent(metaclass=ABCMeta):
    @abstractmethod
    def process(self, args: ParserArgumentsType) -> None:
        pass


class NoSubCmdComponent(BaseSubCmdComponent):
    def process(self, args: ParserArgumentsType) -> None:
        pass
