import json
import os
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from typing import Any, Type, Union, cast
from unittest.mock import Mock, mock_open, patch

import fastapi
import pytest
from fastapi import FastAPI
from fastapi import Response as FastAPIResponse
from flask import Flask
from flask import Request as FlaskRequest
from flask import Response as FlaskResponse

from pymock_api.exceptions import FileFormatNotSupport
from pymock_api.server.application import BaseAppServer, FastAPIServer, FlaskServer
from pymock_api.server.application.response import HTTPResponse as _HTTPResponse

MockerModule = namedtuple("MockerModule", ["module_path", "return_value"])

_General_String_Value: str = "This is test message for PyTest."
_Json_File_Name: str = "test.json"
_Json_File_Content: dict = {"responseCode": "200", "errorMessage": "OK", "content": "This is YouTube home."}
_Not_Exist_File_Name: str = "not_exist.json"
_Not_Json_File_Name: str = "test.yaml"


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


class TestInnerHTTPResponse:
    @pytest.fixture(scope="function")
    def http_resp(self) -> Type[_HTTPResponse]:
        return _HTTPResponse

    def test_response_with_string_data(self, http_resp: Type[_HTTPResponse]):
        resp_data = http_resp.generate(data=_General_String_Value)
        assert resp_data == _General_String_Value, ""

    def test_response_with_json_format_string_data(self, http_resp: Type[_HTTPResponse]):
        json_content_str = json.dumps(_Json_File_Content)
        resp_data = http_resp.generate(data=json_content_str)
        assert resp_data == json.loads(json_content_str), ""

    def test_response_with_json_file_name(self, http_resp: Type[_HTTPResponse]):
        with patch.object(os.path, "exists", return_value=True) as os_path_exists:
            json_content_str = json.dumps(_Json_File_Content)
            with patch("builtins.open", mock_open(read_data=json_content_str)) as mock_file_stream:
                # Run target function to test
                resp_data = http_resp.generate(data=_Json_File_Name)

                # Verify result
                os_path_exists.assert_called_once_with(_Json_File_Name)
                mock_file_stream.assert_called_once_with(_Json_File_Name, "r", encoding="utf-8")
                assert open(_Json_File_Name).read() == json_content_str, ""
                assert resp_data == _Json_File_Content, ""

    def test_response_with_not_exist_json_file_name(self, http_resp: Type[_HTTPResponse]):
        with patch("builtins.open", mock_open(read_data=None)) as mock_file_stream:
            with pytest.raises(FileNotFoundError) as exc_info:
                # Run target function to test
                http_resp.generate(data=_Not_Exist_File_Name)
                # Verify result
                expected_err_msg = f"The target configuration file {_Not_Exist_File_Name} doesn't exist."
                assert str(exc_info) == expected_err_msg, f"The error message should be same as '{expected_err_msg}'."
                mock_file_stream.assert_not_called()

    def test_response_with_not_json_file_name(self, http_resp: Type[_HTTPResponse]):
        with patch("builtins.open", mock_open(read_data=None)) as mock_file_stream:
            with pytest.raises(FileFormatNotSupport) as exc_info:
                # Run target function to test
                http_resp.generate(data=_Not_Json_File_Name)
                # Verify result
                expected_err_msg = f"It doesn't support reading '{', '.join(http_resp.valid_file_format)}' format file."
                assert str(exc_info) == expected_err_msg, f"The error message should be same as '{expected_err_msg}'."
                mock_file_stream.assert_not_called()
