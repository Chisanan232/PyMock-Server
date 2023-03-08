from typing import Type

import pytest
from flask import Flask

from pymock_api.server.application import BaseAppServer, FlaskServer

from ._spec import AppServerTestSpec


class TestFlaskServer(AppServerTestSpec):
    @pytest.fixture(scope="function")
    def app_server(self) -> FlaskServer:
        return FlaskServer()

    @property
    def web_app_object_type(self) -> Type[Flask]:
        return Flask

    def run_target_function(self, app_server: BaseAppServer) -> Flask:
        return app_server.setup()
