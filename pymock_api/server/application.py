"""*Web application with Python web framework*

This module provides which library of Python web framework you could use to set up a web application.
"""

import json
import os
from abc import ABCMeta, abstractmethod
from typing import Any, List, Optional, Union

from .._utils.importing import import_web_lib
from ..exceptions import FileFormatNotSupport
from ..model.api_config import MockAPI, MockAPIs


class BaseAppServer(metaclass=ABCMeta):
    """*Base class for set up web application*"""

    def __init__(self):
        self._web_application = None

    @property
    def web_application(self) -> Any:
        """:obj:`Any`: Property with only getter for the instance of web application, e.g., *Flask*, *FastAPI*, etc."""
        if not self._web_application:
            self._web_application = self.setup()
        return self._web_application

    @abstractmethod
    def setup(self) -> Any:
        """Initial object for setting up web application.

        Returns:
            An object which should be an instance of loading web application server.

        """
        pass

    def create_api(self, mocked_apis: MockAPIs) -> None:
        for api_name, api_config in mocked_apis.apis.items():
            annotate_function_pycode = self._annotate_function(api_name, api_config)
            add_api_pycode = self._add_api(api_name, api_config, base_url=mocked_apis.base.url)
            # pylint: disable=exec-used
            exec(annotate_function_pycode)
            # pylint: disable=exec-used
            exec(add_api_pycode)

    def _annotate_function(self, api_name: str, api_config: MockAPI) -> str:
        return f"""def {api_name}() -> Union[str, dict]:
            return _HTTPResponse.generate(data='{api_config.http.response.value}')
        """

    @abstractmethod
    def _add_api(self, api_name: str, api_config: MockAPI, base_url: Optional[str] = None) -> str:
        pass

    def url_path(self, api_config: MockAPI, base_url: Optional[str] = None) -> str:
        return f"{base_url}{api_config.url}" if base_url else f"{api_config.url}"


class FlaskServer(BaseAppServer):
    """*Build a web application with *Flask**"""

    def setup(self) -> "flask.Flask":
        flask_pkg: "flask" = import_web_lib.flask()
        app: "flask.Flask" = flask_pkg.Flask(__name__)
        return app

    def _add_api(self, api_name: str, api_config: MockAPI, base_url: Optional[str] = None) -> str:
        return f"""self.web_application.route(
            "{self.url_path(api_config, base_url)}", methods=["{api_config.http.request.method}"]
            )({api_name})
        """


class FastAPIServer(BaseAppServer):
    """*Build a web application with *FastAPI**"""

    def setup(self) -> "fastapi.FastAPI":
        fastapi_pkg: "fastapi" = import_web_lib.fastapi()
        app: "fastapi.FastAPI" = fastapi_pkg.FastAPI()
        return app

    def _add_api(self, api_name: str, api_config: MockAPI, base_url: Optional[str] = None) -> str:
        return f"""self.web_application.api_route(
            path="{self.url_path(api_config, base_url)}", methods=["{api_config.http.request.method}"]
            )({api_name})
        """


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
