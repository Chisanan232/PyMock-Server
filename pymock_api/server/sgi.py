"""*The wrapper of application which ruled by SGI (server gateway interface)*

The factory to generate SGI application instance to run Python web framework.
"""

from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar


class BaseCommandOption(metaclass=ABCMeta):
    """*Define what command line options it would have be converted from the arguments by PyMock-API command*"""

    @abstractmethod
    def help(self) -> str:
        """Option *-h* or *--help* of target command.

        Returns:
            A string value which is this option usage.

        """
        pass

    @abstractmethod
    def version(self) -> str:
        """Option *-v* or *--version* of target command.

        Returns:
            A string value which is this option usage.

        """
        pass

    @abstractmethod
    def bind(self, address: str = None, host: str = None, port: str = None) -> str:
        """Option for binding target address includes IPv4 address and port.

        Returns:
            A string value which is this option usage.

        """
        pass

    @abstractmethod
    def workers(self, w: int) -> str:
        """Option for setting how many workers it runs.

        Returns:
            A string value which is this option usage.

        """
        pass

    @abstractmethod
    def log_level(self, level: str) -> str:
        """Option for setting the level of log message to print in console.

        Returns:
            A string value which is this option usage.

        """
        pass


Base_Command_Option_Type = TypeVar("Base_Command_Option_Type", bound=BaseCommandOption)


class BaseSGI(metaclass=ABCMeta):
    """*Base class of SGI*"""

    @classmethod
    @abstractmethod
    def server(cls):
        """Initial and set up an application via SGI application.

        Returns:
            An object which is SGI application.

        """
        pass

    @property
    @abstractmethod
    def cmd_entry_point(self) -> str:
        """The command line program name.

        Returns:
            A string value about the command line.

        """
        pass

    @property
    @abstractmethod
    def cmd_options(self) -> Generic[Base_Command_Option_Type]:
        """The command line options.

        Returns:
            An implementation of subclass of BaseCommandLineOption which has its options.

        """
        pass


class WSGICmdOption(BaseCommandOption):
    """*WSGI tool *gunicorn* command line options*

    Note:

    0-1. -h, --help    show this help message and exit
    0-2. -v, --version    show program's version number and exit

    1. -b ADDRESS, --bind ADDRESS    The socket to bind. [['127.0.0.1:8000']]

    2. -w INT, --workers INT    The number of worker processes for handling requests. [1]

    3. --log-level LEVEL    The granularity of Error log outputs. [info]
    """

    def help(self) -> str:
        return "--help"

    def version(self) -> str:
        return "--version"

    def bind(self, address: str = None, host: str = None, port: str = None) -> str:
        if address:
            binding_addr = address
        elif host and port:
            binding_addr = f"{host}:{port}"
        else:
            raise ValueError("")
        return f"--bind {binding_addr}"

    def workers(self, w: int) -> str:
        return f"--workers {w}"

    def log_level(self, level: str) -> str:
        return f"--log-level {level}"


class WSGI(BaseSGI):
    """*WSGI application*

    This module for generating WSGI (Web Server Gateway Interface) application by Python tool *gunicorn*.
    """

    @classmethod
    def server(cls):
        from gunicorn.app.wsgiapp import WSGIApplication

        return WSGIApplication("%(prog)s [OPTIONS] [APP_MODULE]")

    @property
    def cmd_entry_point(self) -> str:
        return "gunicorn"

    @property
    def cmd_options(self) -> WSGICmdOption:
        return WSGICmdOption()
