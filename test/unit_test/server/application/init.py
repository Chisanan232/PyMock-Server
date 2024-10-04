from abc import ABCMeta, abstractmethod
from collections import namedtuple
from typing import Any, Type, Union, cast
from unittest.mock import Mock, patch

import fastapi
import pytest
from fastapi import FastAPI
from fastapi import Response as FastAPIResponse
from flask import Flask
from flask import Request as FlaskRequest
from flask import Response as FlaskResponse

from pymock_server.server.application import BaseAppServer, FastAPIServer, FlaskServer

MockerModule = namedtuple("MockerModule", ["module_path", "return_value"])


class FakeFlask(Flask):
    pass


class FakeFastAPI(FastAPI):
    pass


class DummyFlaskRequest(FlaskRequest):
    def __init__(self):
        pass
        # super().__init__(environ={})


class AppServerTestSpec(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def sut(self) -> BaseAppServer:
        pass

    @property
    @abstractmethod
    def expected_sut_type(self) -> Any:
        pass

    @property
    @abstractmethod
    def mocker(self) -> MockerModule:
        pass

    def test_generating_instance_function(self, sut: BaseAppServer):
        with patch(self.mocker.module_path, return_value=self.mocker.return_value) as instantiate_ps:
            web_app = sut.setup()
            instantiate_ps.assert_called_once()
            assert isinstance(
                web_app, self.expected_sut_type
            ), f"The web application server it generates should be *{self.expected_sut_type}* type object."

    @abstractmethod
    def _mock_request(self, method: str, api_params: dict) -> Mock:
        pass

    @abstractmethod
    def _run_request_process_func(self, sut: BaseAppServer, **kwargs) -> Any:
        pass

    @abstractmethod
    def _get_response_content(self, response: Any) -> Union[str, bytes, dict]:
        pass

    @property
    @abstractmethod
    def _expected_response_type(self) -> Type[Any]:
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

    def _mock_request(self, method: str, api_params: dict) -> Mock:
        request = Mock()
        request.path = "/test-api-path"
        request.method = method
        request.args = api_params
        return request

    def _run_request_process_func(self, sut: BaseAppServer, **kwargs) -> "flask.Response":
        return sut._request_process()

    def _get_response_content(self, response: "flask.Response") -> Union[str, bytes, dict]:
        return response.data or response.json

    @property
    def _expected_response_type(self) -> Type[FlaskResponse]:
        return FlaskResponse


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

    def _mock_request(self, method: str, api_params: dict) -> Mock:
        route_prop = Mock()
        route_prop.path = "/test-api-path"

        request = Mock()
        request.scope = {
            "root_path": "",
            "route": route_prop,
        }

        request.method = method

        # Just for testing, source code won't have any usage like this
        request.api_parameters = api_params
        return request

    def _run_request_process_func(self, sut: BaseAppServer, **kwargs) -> "fastapi.Response":
        class DummyModel:
            pass

        model = DummyModel()
        for k, v in cast(dict, kwargs["request"].api_parameters).items():
            setattr(model, k, v)
        return sut._request_process(model=model, request=kwargs["request"])

    def _get_response_content(self, response: "fastapi.Response") -> Union[str, bytes, dict]:
        return response.body

    @property
    def _expected_response_type(self) -> Type[FastAPIResponse]:
        return FastAPIResponse
