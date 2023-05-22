import json
import os
import re
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from typing import Any, List, Optional, Type, Union, cast
from unittest.mock import MagicMock, Mock, PropertyMock, call, mock_open, patch

import fastapi
import pytest
from fastapi import FastAPI
from fastapi import Request as FastAPIRequest
from fastapi import Response as FastAPIResponse
from flask import Flask
from flask import Request as FlaskRequest
from flask import Response as FlaskResponse

from pymock_api.exceptions import FileFormatNotSupport
from pymock_api.model.api_config import APIParameter, MockAPI
from pymock_api.server.application import (
    BaseAppServer,
    FastAPIServer,
    FlaskServer,
    _HTTPResponse,
)

from ..._values import _Test_API_Parameter, _Test_API_Parameters, _Test_URL, _TestConfig

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

    def test_generate_pycode_about_annotating_function(self, sut: BaseAppServer):
        for_test_api_name = "Function name"
        for_test_resp = "Response value for PyTest."
        api = Mock(MockAPI(url=Mock(), http=Mock()))
        api.http.request.parameters = [APIParameter().deserialize(p) for p in _Test_API_Parameters]
        api.http.response.value = for_test_resp

        annotate_function_pycode = sut._annotate_function(api_name=for_test_api_name, api_config=api)

        assert for_test_api_name in annotate_function_pycode and for_test_resp in annotate_function_pycode

    @pytest.mark.parametrize(
        ("method", "api_params", "error_msg_like", "expected_status_code"),
        [
            ("GET", {"param1": "any_format"}, None, 200),
            ("GET", {"miss_param": "miss_param"}, ["Miss required parameter"], 400),
            ("GET", {"param1": None}, ["Miss required parameter"], 400),
            ("GET", {"param1": 123}, ["type of data", "is different"], 400),
            ("GET", {"param1": "incorrect_format"}, ["format of data", "is incorrect"], 400),
        ],
    )
    def test_request_process(
        self,
        method: str,
        api_params: dict,
        error_msg_like: Optional[List[str]],
        expected_status_code: int,
        sut: BaseAppServer,
    ):
        # Mock request
        request = self._mock_request(method=method, api_params=api_params)

        # Mock API attribute and function
        sut._api_params = {"/test-api-path": MockAPI().deserialize(_TestConfig.Mock_API)}
        sut._get_current_request = MagicMock(return_value=request)

        # Run target function
        response = self._run_request_process_func(sut, request=request)

        # Verify
        assert isinstance(response, self._expected_response_type)
        assert response.status_code == expected_status_code
        if response.status_code != 200:
            response_content = self._get_response_content(response)
            response_str = response_content.decode("utf-8") if isinstance(response_content, bytes) else response_content
            regular = r""
            for er_msg_f in error_msg_like:
                regular += r".{0,512}" + re.escape(er_msg_f)
            assert re.search(regular, response_str, re.IGNORECASE)

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

    @pytest.mark.parametrize("base_url", [None, "Has base URL"])
    def test_generate_pycode_about_adding_api(self, sut: BaseAppServer, base_url: Optional[str]):
        for_test_api_name = "Function name"
        for_test_url = "this is an url path"
        for_test_req_method = "HTTP method"
        api = Mock(MockAPI(url=Mock(), http=Mock()))
        api.url = for_test_url
        api.http.request.method = for_test_req_method

        add_api_pycode = sut._add_api(api_name=for_test_api_name, api_config=api, base_url=base_url)

        expected_url = f"{base_url}{for_test_url}" if base_url else for_test_url
        assert expected_url in add_api_pycode and for_test_req_method in add_api_pycode


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
