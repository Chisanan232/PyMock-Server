from abc import ABCMeta, abstractmethod
from collections import namedtuple
from typing import Any, Type
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from flask import Flask

from pymock_api.server.application import BaseAppServer, FastAPIServer, FlaskServer

MockerModule = namedtuple("MockerModule", ["module_path", "return_value"])


class AppServerTestSpec(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def sut(self) -> BaseAppServer:
        pass

    @property
    @abstractmethod
    def expected_sut_type(self) -> Any:
        pass

    @abstractmethod
    def run_target_function(self, sut: BaseAppServer) -> Any:
        pass

    @property
    @abstractmethod
    def mocker(self) -> MockerModule:
        pass

    def test_generating_instance_function(self, sut: BaseAppServer):
        with patch(self.mocker.module_path, return_value=self.mocker.return_value) as instantiate_ps:
            web_app = self.run_target_function(sut)
            instantiate_ps.assert_called_once()
            assert isinstance(
                web_app, self.expected_sut_type
            ), f"The web application server it generates should be *{self.expected_sut_type}* type object."


class FakeFlask(Flask):
    pass


class FakeFastAPI(FastAPI):
    pass


class TestFlaskServer(AppServerTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> FlaskServer:
        return FlaskServer()

    @property
    def expected_sut_type(self) -> Type[Flask]:
        return Flask

    @property
    def mocker(self) -> MockerModule:
        return MockerModule(module_path="flask.Flask", return_value=FakeFlask("PyTest-Used"))

    def run_target_function(self, sut: FlaskServer) -> Flask:
        return sut.setup()


class TestFastAPIServer(AppServerTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> FastAPIServer:
        return FastAPIServer()

    @property
    def expected_sut_type(self) -> Type[FastAPI]:
        return FastAPI

    @property
    def mocker(self) -> MockerModule:
        return MockerModule(module_path="fastapi.FastAPI", return_value=FakeFastAPI())

    def run_target_function(self, sut: FastAPIServer) -> Flask:
        return sut.setup()
