from abc import ABCMeta, abstractmethod
from typing import Generic

from ._model import Command, CommandOptions, ParserArguments
from .cmdoption import Base_Command_Option_Type, WSGICmdOption


class BaseSGICmd(metaclass=ABCMeta):
    """*Base class of SGI*"""

    def generate(self, parser_args: ParserArguments) -> Command:
        """Generate an object about command line for running finally.

        Args:
            parser_args (ParserArguments): The data object which has been parsed by arguments of current running command
                line.

        Returns:
            An **Command** type object.

        """
        return Command(
            entry_point=self.entry_point,
            options=CommandOptions(
                bind=self.options.bind(address=parser_args.bind),
                workers=self.options.workers(w=parser_args.workers),
                log_level=self.options.log_level(level=parser_args.log_level),
            ),
        )

    @property
    @abstractmethod
    def entry_point(self) -> str:
        """The command line program name.

        Returns:
            A string value about the command line.

        """
        pass

    @property
    @abstractmethod
    def options(self) -> Generic[Base_Command_Option_Type]:
        """The command line options.

        Returns:
            An implementation of subclass of BaseCommandLineOption which has its options.

        """
        pass


class WSGICmd(BaseSGICmd):
    """*WSGI application*

    This module for generating WSGI (Web Server Gateway Interface) application by Python tool *gunicorn*.
    """

    @property
    def entry_point(self) -> str:
        return "gunicorn"

    @property
    def options(self) -> WSGICmdOption:
        return WSGICmdOption()
