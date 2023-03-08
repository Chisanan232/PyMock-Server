from typing import Any, Type

import pytest
from flask import Flask

from pymock_api.server.application import BaseAppServer, FlaskServer

from ._spec import AppServerTestSpec, MockerModule


class FakeFlask(Flask):
    pass


class TestFlaskServer(AppServerTestSpec):
    @pytest.fixture(scope="function")
    def app_server(self) -> FlaskServer:
        return FlaskServer()

    @property
    def web_app_object_type(self) -> Type[Flask]:
        return Flask

    @property
    def mocker(self) -> MockerModule:
        return MockerModule(module_path="flask.Flask", return_value=FakeFlask("PyTest-Used"))

    def run_target_function(self, app_server: BaseAppServer) -> Flask:
        return app_server.setup()
