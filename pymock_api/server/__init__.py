"""*The details processing of application*

The processing of application includes configure settings, initial objects, set up application by SGI (Server Gateway
Interface) tool, e.g., *gunicorn*, etc.
"""

import os

from .._utils.importing import ensure_importing, import_web_lib
from .application import BaseAppServer, FastAPIServer, FlaskServer
from .mock import MockHTTPServer
from .sgi.cmd import WSGIServer

flask_app: "flask.Flask" = None
fastapi_app: "fastapi.FastAPI" = None


def create_flask_app() -> "flask.Flask":
    load_app.by_flask()
    return flask_app


def create_fastapi_app() -> "fastapi.FastAPI":
    load_app.by_fastapi()
    return fastapi_app


class load_app:
    """*Set up and safely load the web application with Python web framework*

    Safely load application with different Python web frameworks if it could. It would try to load the web application
    if it could import the library of Python web framework, e.g., *flask*, successfully without any issue. Or it won't
    do anything.
    """

    @classmethod
    @ensure_importing(import_web_lib.flask)
    def by_flask(cls) -> None:
        """Set up web application with *Flask*.

        Returns:
            None

        """
        global flask_app
        config = cls._get_config_path()
        flask_app = cls._initial_mock_server(config_path=config, app_server=FlaskServer()).web_app

    @classmethod
    @ensure_importing(import_web_lib.fastapi)
    def by_fastapi(cls) -> None:
        """Set up web application with *FastAPI*.

        Returns:
            None

        """
        global fastapi_app
        config = cls._get_config_path()
        fastapi_app = cls._initial_mock_server(config_path=config, app_server=FastAPIServer()).web_app

    @classmethod
    def _get_config_path(cls) -> str:
        """Get the configuration file path by environment variable in OS runtime environment.

        Returns:
            A string value about the configuration file path.

        """
        return os.environ.get("MockAPI_Config", "api.yaml")

    @classmethod
    def _initial_mock_server(cls, config_path: str, app_server: BaseAppServer) -> MockHTTPServer:
        """Instantiate the mocked web server.

        Args:
            config_path (str): The configuration file path.
            app_server (BaseAppServer): The web application type.

        Returns:
            A **MockHTTPServer** type object.

        """
        return MockHTTPServer(config_path=config_path, app_server=app_server, auto_setup=True)
