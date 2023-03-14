"""*The details processing of application*

The processing of application includes configure settings, initial objects, set up application by SGI (Server Gateway
Interface) tool, e.g., *gunicorn*, etc.
"""

import os
from typing import Callable

import flask

from .application import BaseAppServer, FlaskServer
from .mock import MockHTTPServer
from .sgi.cmd import WSGICmd

flask_app: "flask.Flask" = None


def create_flask_app() -> "flask.Flask":
    load_app.with_flask()
    return flask_app


class load_app:
    """*Safely load application with Python web frameworks*

    Safely load application with different Python web frameworks if it could. It would try to load the web application
    if it could import the library of Python web framework, e.g., *flask*, successfully without any issue. Or it won't
    do anything.
    """

    @classmethod
    def with_flask(cls) -> None:
        """Load the mocked web application with Python web framework *Flask*.

        Returns:
            None

        """

        def _import() -> None:
            import flask

        def _load_app() -> None:
            SetupApp.by_flask()

        cls._load_app_by_importing(import_callback=_import, import_success_callback=_load_app)

    @staticmethod
    def _load_app_by_importing(
        import_callback: Callable, import_success_callback: Callable, import_err_callback: Callable = None
    ) -> None:
        """Load application if importing works finely without any issue. Or it will do nothing.

        Args:
            import_callback (Callable): The callback function to import module.
            import_success_callback (Callable): The callback function which would be run after importing successfully.
            import_err_callback (Callable): The callback function which would be run if it failed at importing.

        Returns:
            None

        """
        try:
            import_callback()
        except ImportError as e:
            if import_err_callback:
                import_err_callback(e)
        else:
            import_success_callback()


class SetupApp:
    """*Set up the web application with Python web framework*"""

    @classmethod
    def by_flask(cls) -> None:
        """Set up web application with *Flask*.

        Returns:
            None

        """
        global flask_app
        config = cls._get_config_path()
        import pymock_api

        flask_app = cls._initial_mock_server(config_path=config, app_server=FlaskServer()).web_app
        pymock_api.app = flask_app

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
