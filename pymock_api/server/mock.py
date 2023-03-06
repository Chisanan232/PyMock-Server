import json
import os
from typing import List, Union

from .._utils import load_config
from ..exceptions import FileFormatNotSupport
from ..model.api_config import APIConfig, MockAPIs
from .application import BaseAppServer, FlaskServer


class MockHTTPServer:
    def __init__(self, config_path: str = None, app_server: BaseAppServer = None, auto_setup: bool = False):
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
    def web_app(self):
        if not self._web_application:
            self._web_application = self._app_server.setup()
        return self._web_application

    def create_apis(self, mocked_apis: MockAPIs) -> None:
        for api_name, api_config in mocked_apis.apis.items():
            exec(
                f"""def {api_name}() -> Union[str, dict]:
                return _HTTPResponse.generate(data='{api_config.http.response.value}')
            """
            )
            exec(
                f"""self.web_app.route(
                    "{mocked_apis.base.url}{api_config.url}", methods=["{api_config.http.request.method}"]
                )({api_name}) """
            )


class _HTTPResponse:

    valid_file_format: List[str] = ["json"]

    @classmethod
    def generate(cls, data: str) -> Union[str, dict]:
        try:
            return json.loads(data)
        except:  # pylint: disable=broad-except
            if cls._is_file(path=data):
                return cls._read_file(path=data)
        return data

    @classmethod
    def _is_file(cls, path: str) -> bool:
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
        exist_file = os.path.exists(path)
        if not exist_file:
            raise FileNotFoundError(f"The target configuration file {path} doesn't exist.")

        with open(path, "r", encoding="utf-8") as file_stream:
            data = file_stream.read()
        return json.loads(data)
