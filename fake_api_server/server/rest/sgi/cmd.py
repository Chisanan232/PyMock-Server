from abc import ABCMeta, abstractmethod

from fake_api_server.model.command.rest_server.cmd_args import SubcmdRunArguments

from ._model import Command, CommandOptions
from .cmdoption import ASGICmdOption, BaseCommandOption, WSGICmdOption


class BaseSGIServer(metaclass=ABCMeta):
    """*Base class of SGI*"""

    def __init__(self, app: str):
        if not app:
            raise ValueError("The application instance path cannot be None or empty.")
        self._app = app
        self._SGI_Command_Option: BaseCommandOption = self._init_cmd_option()

    @abstractmethod
    def _init_cmd_option(self) -> BaseCommandOption:
        pass

    def run(self, parser_args: SubcmdRunArguments) -> None:
        command_line = self.generate(parser_args)
        command_line.run()

    def generate(self, parser_args: SubcmdRunArguments) -> Command:
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
                daemon=parser_args.daemon,
                access_log_file=parser_args.access_log_file,
            ),
        )

    @property
    @abstractmethod
    def entry_point(self) -> str:
        """The command line program name.

        Returns:
            A string value about the command line.

        """

    @property
    def options(self) -> BaseCommandOption:
        """The command line options.

        Returns:
            An implementation of subclass of BaseCommandLineOption which has its options.

        """
        return self._SGI_Command_Option


class WSGIServer(BaseSGIServer):
    """*WSGI application*

    This module for generating WSGI (Web Server Gateway Interface) application by Python tool *gunicorn*.

    .. note: Example usage of WSGI tool *gunicorn*

        PyFake-API-Server would generate the command line as string value which is valid to run as following:

        .. code-block: shell

            >>> gunicorn --bind 127.0.0.1:9672 'fake_api_server.server:create_flask_app()'

    """

    def _init_cmd_option(self) -> BaseCommandOption:
        return WSGICmdOption()

    @property
    def entry_point(self) -> str:
        return "gunicorn"


class ASGIServer(BaseSGIServer):
    """*ASGI application*

    This module for generating ASGI (Asynchronous Server Gateway Interface) application by Python tool *uvicorn*.

    .. note: Example usage of WSGI tool *gunicorn*

        PyFake-API-Server would generate the command line as string value which is valid to run as following:

        .. code-block: shell

            >>> uvicorn --host 127.0.0.1 --port 9672 --factory 'fake_api_server.server:create_flask_app()'

    """

    def _init_cmd_option(self) -> BaseCommandOption:
        return ASGICmdOption()

    @property
    def entry_point(self) -> str:
        return "uvicorn --factory"
