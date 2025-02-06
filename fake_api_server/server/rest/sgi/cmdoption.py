import re
from abc import ABCMeta, abstractmethod
from typing import Optional, TypeVar


class BaseCommandOption(metaclass=ABCMeta):
    """*Define what command line options it would have be converted from the arguments by PyFake-API-Server command*"""

    def help(self) -> str:
        """Option *-h* or *--help* of target command.

        Returns:
            A string value which is this option usage.

        """
        return "--help"

    def version(self) -> str:
        """Option *-v* or *--version* of target command.

        Returns:
            A string value which is this option usage.

        """
        return "--version"

    @abstractmethod
    def bind(self, address: Optional[str] = None, host: Optional[str] = None, port: Optional[str] = None) -> str:
        """Option for binding target address includes IPv4 address and port.

        Returns:
            A string value which is this option usage.

        """

    @abstractmethod
    def workers(self, w: int) -> str:
        """Option for setting how many workers it runs.

        Returns:
            A string value which is this option usage.

        """

    @abstractmethod
    def log_level(self, level: str) -> str:
        """Option for setting the level of log message to print in console.

        Returns:
            A string value which is this option usage.

        """

    def _is_valid_address(self, address: str) -> bool:
        if not re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", str(address)):
            raise ValueError(
                "The address info is invalid. Please entry value format should be as <IPv4 address>:<Port>."
            )
        return True


Base_Command_Option_Type = TypeVar("Base_Command_Option_Type", bound=BaseCommandOption)


class WSGICmdOption(BaseCommandOption):
    """*WSGI tool *gunicorn* command line options*

    Note:

    0-1. -h, --help    show this help message and exit
    0-2. -v, --version    show program's version number and exit

    1. -b ADDRESS, --bind ADDRESS    The socket to bind. [['127.0.0.1:8000']]

    2. -w INT, --workers INT    The number of worker processes for handling requests. [1]

    3. --log-level LEVEL    The granularity of Error log outputs. [info]
    """

    def bind(self, address: Optional[str] = None, host: Optional[str] = None, port: Optional[str] = None) -> str:
        if address:
            self._is_valid_address(address)
            binding_addr = address
        elif host and port:
            binding_addr = f"{host}:{port}"
        else:
            raise ValueError("There are 2 ways to pass arguments: using *address* or using *host* and *port*.")
        return f"--bind {binding_addr}"

    def workers(self, w: int) -> str:
        return f"--workers {w}"

    def log_level(self, level: str) -> str:
        return f"--log-level {level}"


class ASGICmdOption(BaseCommandOption):
    """*ASGI application*

    This module for generating WSGI (Web Server Gateway Interface) application by Python tool *gunicorn*.

    Note:

    0-1. --help    Show this message and exit.
    0-2. --version    Display the uvicorn version and exit.

    1. --host TEXT    Bind socket to this host.  [default: 127.0.0.1]
       --port INTEGER    Bind socket to this port.  [default: 8000]

    2. --workers INTEGER    Number of worker processes. Defaults to the $WEB_CONCURRENCY environment variable if available, or 1. Not valid with --reload

    3. --log-level [critical|error|warning|info|debug|trace] Log level. [default: info]
    """

    def bind(self, address: Optional[str] = None, host: Optional[str] = None, port: Optional[str] = None) -> str:
        if address:
            self._is_valid_address(address)
            address_info = address.split(":")
            binding_host = address_info[0]
            binding_port = address_info[1]
        elif host and port:
            binding_host = host
            binding_port = port
        else:
            raise ValueError("There are 2 ways to pass arguments: using *address* or using *host* and *port*.")
        return f"--host {binding_host} --port {binding_port}"

    def workers(self, w: int) -> str:
        return f"--workers {w}"

    def log_level(self, level: str) -> str:
        return f"--log-level {level}"
