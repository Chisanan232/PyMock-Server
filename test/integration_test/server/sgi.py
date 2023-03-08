from typing import Any, Type

import pytest
from gunicorn.app.wsgiapp import WSGIApplication

from pymock_api.server.sgi import WSGI, BaseSGI

from ._spec import AppServerTestSpec, MockerModule


class FakeWSGIApp(WSGIApplication):
    def load_config(self):
        """Do nothing"""


class TestWSGIApp(AppServerTestSpec):
    @pytest.fixture(scope="function")
    def app_server(self) -> WSGI:
        return WSGI()

    @property
    def web_app_object_type(self) -> Type[WSGIApplication]:
        return WSGIApplication

    @property
    def mocker(self) -> MockerModule:
        return MockerModule(module_path="gunicorn.app.wsgiapp.WSGIApplication", return_value=FakeWSGIApp())

    def run_target_function(self, app_server: BaseSGI) -> WSGIApplication:
        return app_server.server()
