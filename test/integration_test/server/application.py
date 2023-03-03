from abc import ABCMeta, abstractmethod
from typing import Any, Type

import pytest
from flask import Flask

from pymock_api.server.application import BaseAppServer, FlaskServer


class AppServerTestSpec(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def app_server(self) -> BaseAppServer:
        pass

    @property
    @abstractmethod
    def web_app_object_type(self) -> Any:
        pass

    def test_setup(self, app_server: BaseAppServer):
        web_app = app_server.setup()
        assert isinstance(
            web_app, self.web_app_object_type
        ), f"The web application server it generates should be *{self.web_app_object_type}* type object."


class TestFlaskServer(AppServerTestSpec):
    @pytest.fixture(scope="function")
    def app_server(self) -> FlaskServer:
        return FlaskServer()

    @property
    def web_app_object_type(self) -> Type[Flask]:
        return Flask
