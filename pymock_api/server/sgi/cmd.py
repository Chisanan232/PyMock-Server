from abc import ABCMeta, abstractmethod
from typing import Generic

from .cmdoption import Base_Command_Option_Type, WSGICmdOption


class BaseSGICmd(metaclass=ABCMeta):
    """*Base class of SGI*"""

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
