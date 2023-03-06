"""*The HTTP application server for mocking APIs*

This module provides objects for mocking APIs as a web application with different Python framework.
"""

import json
import os
from typing import Any, List, Union

from .._utils import load_config
from ..exceptions import FileFormatNotSupport
from ..model.api_config import APIConfig, MockAPIs
from .application import BaseAppServer, FlaskServer


class MockHTTPServer:
    """*Mocking APIs as web application with HTTP*

    It provides the web application which mocks all APIs from configuration with one specific Python web framework. In
    default, it would use *Flask* to set up the web server to provide the APIs.
    """

    def __init__(self, config_path: str = None, app_server: BaseAppServer = None, auto_setup: bool = False):
        """

        Args:
            config_path (str): The file path of configuration about mocked APIs. In default, it would search file
                *api.yaml* in the current directory.
            app_server (BaseAppServer): Which web application to use to set up the web application to mock APIs. In
                generally, it must be the *pymock_api.application.BaseAppServer* type object. In default, it would use
                *Flask* to set up the web application.
            auto_setup (auto_setup): Initial and create mocked APIs when instantiate this object. In default, it's
                ``False``.
        """
        if not config_path:
            config_path = "api.yaml"
        self._config_path = config_path
        self._api_config: APIConfig = load_config(config_path=self._config_path)

        if app_server and not isinstance(app_server, BaseAppServer):
            raise TypeError(f"The instance {app_server} must be *pymock_api.application.BaseAppServer* type object.")
        if not app_server:
            app_server = FlaskServer()
        self._app_server = app_server
        self._web_application = None

        if auto_setup:
            mocked_apis = self._api_config.apis
            self.create_apis(mocked_apis=mocked_apis)

    @property
    def web_app(self) -> Any:
        """:obj:`Any`: Property with only getter for the instance of web application, e.g., *Flask*, *FastAPI*, etc."""
        if not self._web_application:
            self._web_application = self._app_server.setup()
        return self._web_application

    def create_apis(self, mocked_apis: MockAPIs) -> None:
        """Initial and create all mocked APIs from the data objects which be generated by configuration.

        Args:
            mocked_apis (MockAPIs): The data object of mocked APIs configuration which be generated by utility function
                *pymock_api._utils.load_config*.

        Returns:
            None

        """
        for api_name, api_config in mocked_apis.apis.items():
            # pylint: disable=exec-used
            exec(
                f"""def {api_name}() -> Union[str, dict]:
                return _HTTPResponse.generate(data='{api_config.http.response.value}')
            """
            )
            # pylint: disable=exec-used
            exec(
                f"""self.web_app.route(
                    "{mocked_apis.base.url}{api_config.url}", methods=["{api_config.http.request.method}"]
                )({api_name}) """
            )


class _HTTPResponse:
    """*Data processing of HTTP response for mocked HTTP application*

    Handle the HTTP response value from the mocked APIs configuration.
    """

    valid_file_format: List[str] = ["json"]

    @classmethod
    def generate(cls, data: str) -> Union[str, dict]:
        """Generate the HTTP response by the data. It would try to parse it as JSON format data in the beginning. If it
        works, it returns the handled data which is JSON format. But if it gets fail, it would change to check whether
        it is a file path or not. If it is, it would search and read the file to get the content value and parse it to
        return. If it isn't, it returns the data directly.

        Args:
            data (str): The HTTP response value.

        Returns:
            A string type or dict type value.

        """
        try:
            return json.loads(data)
        except:  # pylint: disable=broad-except, bare-except
            if cls._is_file(path=data):
                return cls._read_file(path=data)
        return data

    @classmethod
    def _is_file(cls, path: str) -> bool:
        """Check whether the data is a file path or not.

        Args:
            path (str): A string type value.

        Returns:
            It returns ``True`` if it is a file path and the file exists, nor it returns ``False``.

        """
        path_sep_by_dot = path.split(".")
        path_sep_by_dot_without_non = list(filter(lambda e: e, path_sep_by_dot))
        if len(path_sep_by_dot_without_non) > 1:
            support = path_sep_by_dot[-1] in cls.valid_file_format
            if not support:
                raise FileFormatNotSupport(cls.valid_file_format)
            return support
        else:
            return False

    @classmethod
    def _read_file(cls, path: str) -> dict:
        """Read file by the path to get its content and parse it as JSON format value.

        Args:
            path (str): The file path which records JSON format value.

        Returns:
            A dict type value which be parsed from JSON format value.

        """
        exist_file = os.path.exists(path)
        if not exist_file:
            raise FileNotFoundError(f"The target configuration file {path} doesn't exist.")

        with open(path, "r", encoding="utf-8") as file_stream:
            data = file_stream.read()
        return json.loads(data)
