from abc import ABCMeta, abstractmethod

from ..model.cmd_args import ParserArguments


class BaseSubCmdComponent(metaclass=ABCMeta):
    @abstractmethod
    def process(self, args: ParserArguments) -> None:
        pass
