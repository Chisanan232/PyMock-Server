"""*Web application with Python web framework*

This module provides which library of Python web framework you could use to set up a web application.
"""

from abc import ABCMeta, abstractmethod
from typing import Any

from .._utils.importing import import_web_lib


class BaseAppServer(metaclass=ABCMeta):
    """*Base class for set up web application*"""

    @abstractmethod
    def setup(self) -> Any:
        """Initial object for setting up web application.

        Returns:
            An object which should be an instance of loading web application server.

        """
        pass


class FlaskServer(BaseAppServer):
    """*Build a web application with *Flask**"""

    def setup(self) -> "flask.Flask":
        flask_pkg: "flask" = import_web_lib.flask()
        app: "flask.Flask" = flask_pkg.Flask(__name__)
        return app
