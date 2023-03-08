from typing import Type
from unittest.mock import patch

import pytest
from gunicorn.app.wsgiapp import WSGIApplication

from pymock_api.server.sgi import WSGI, BaseSGI

from ._spec import AppServerTestSpec


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

    def run_target_function(self, app_server: BaseSGI) -> WSGIApplication:
        with patch.object(app_server, "server", return_value=FakeWSGIApp()):
            return app_server.server()
