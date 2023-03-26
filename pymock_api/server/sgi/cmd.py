from abc import ABCMeta, abstractmethod
from typing import Generic

from ...model.cmd_args import ParserArguments
from ._model import Command, CommandOptions
from .cmdoption import ASGICmdOption, Base_Command_Option_Type, WSGICmdOption


class BaseSGIServer(metaclass=ABCMeta):
    """*Base class of SGI*"""

    _SGI_Command_Option: Generic[Base_Command_Option_Type] = None

    def __init__(self, app: str):
        if not app:
            raise ValueError("The application instance path cannot be None or empty.")
        self._app = app

    def run(self, parser_args: ParserArguments) -> None:
        command_line = self.generate(parser_args)
        command_line.run()

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
            app=self._app,
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


class WSGIServer(BaseSGIServer):
    """*WSGI application*

    This module for generating WSGI (Web Server Gateway Interface) application by Python tool *gunicorn*.

    .. note: Example usage of WSGI tool *gunicorn*

        PyMock-API would generate the command line as string value which is valid to run as following:

        .. code-block: shell

            >>> gunicorn --bind 127.0.0.1:9672 'pymock_api.server:create_flask_app()'

    """

    @property
    def entry_point(self) -> str:
        return "gunicorn"

    @property
    def options(self) -> WSGICmdOption:
        if not self._SGI_Command_Option:
            self._SGI_Command_Option = WSGICmdOption()
        return self._SGI_Command_Option


class ASGIServer(BaseSGIServer):
    """*ASGI application*

    This module for generating ASGI (Asynchronous Server Gateway Interface) application by Python tool *uvicorn*.

    .. note: Example usage of WSGI tool *gunicorn*

        PyMock-API would generate the command line as string value which is valid to run as following:

        .. code-block: shell

            >>> uvicorn --host 127.0.0.1 --port 9672 --factory 'pymock_api.server:create_flask_app()'

    """

    @property
    def entry_point(self) -> str:
        return "uvicorn --factory"

    @property
    def options(self) -> ASGICmdOption:
        if not self._SGI_Command_Option:
            self._SGI_Command_Option = ASGICmdOption()
        return self._SGI_Command_Option
