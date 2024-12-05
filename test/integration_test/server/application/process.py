import logging
import re
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from typing import Any, List, Optional, Type, Union, cast
from unittest.mock import MagicMock, Mock

import fastapi
import pytest
from fastapi import FastAPI
from fastapi import Response as LibFastAPIResponse
from flask import Flask
from flask import Response as LibFlaskResponse

from pymock_server.model import MockAPI
from pymock_server.server.application.process import BaseHTTPProcess, HTTPRequestProcess
from pymock_server.server.application.request import (
    BaseCurrentRequest,
    FastAPIRequest,
    FlaskRequest,
)
from pymock_server.server.application.response import (
    BaseResponse,
    FastAPIResponse,
    FlaskResponse,
)

from ...._values import (
    _Google_Home_Value,
    _Post_Google_Home_Value,
    _Test_Home_With_Customize_Format_Req_Param,
    _Test_Home_With_Enums_Format_Req_Param,
    _Test_Home_With_General_Format_Req_Param,
)

logger = logging.getLogger(__name__)

MockerModule = namedtuple("MockerModule", ["module_path", "return_value"])


class FakeFlask(Flask):
    pass


class FakeFastAPI(FastAPI):
    pass


class DummyFlaskRequest(FlaskRequest):
    def __init__(self):
        pass
        # super().__init__(environ={})


class HTTPProcessTestSpec(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def request_utils(self) -> BaseCurrentRequest:
        pass

    @pytest.fixture(scope="function")
    @abstractmethod
    def response_utils(self) -> BaseResponse:
        pass

    @pytest.fixture(scope="function")
    @abstractmethod
    def sut(self) -> Type[BaseHTTPProcess]:
        pass

    @property
    @abstractmethod
    def expected_sut_type(self) -> Any:
        pass

    @property
    @abstractmethod
    def mocker(self) -> MockerModule:
        pass

    @pytest.mark.parametrize(
        ("path", "method", "api_params", "error_msg_like", "expected_status_code"),
        [
            # Valid request with *GET* HTTP method
            (
                "/test-api-path",
                "GET",
                {"param1": "any_format", "single_iterable_param": ["param1", "param2", "param3"]},
                None,
                200,
            ),
            # Invalid request with *GET* HTTP method
            ("/test-api-path", "GET", {"miss_param": "miss_param"}, ["Miss required parameter"], 400),
            ("/test-api-path", "GET", {"param1": None}, ["Miss required parameter"], 400),
            ("/test-api-path", "GET", {"param1": 123}, ["type of data", "is different"], 400),
            (
                "/test-api-path",
                "GET",
                {"param1": "any_format", "single_iterable_param": [123]},
                ["type of data", "is different"],
                400,
            ),
            ("/test-api-path", "GET", {"param1": "incorrect_format"}, ["format of data", "is incorrect"], 400),
            # Valid request with *POST* HTTP method
            (
                "/test-api-path",
                "POST",
                {"param1": "any_format", "iterable_param": [{"name": "param1", "value": "value1"}]},
                None,
                200,
            ),
            # Invalid request with *POST* HTTP method
            ("/test-api-path", "POST", {"miss_param": "miss_param"}, ["Miss required parameter"], 400),
            ("/test-api-path", "POST", {"param1": None}, ["Miss required parameter"], 400),
            ("/test-api-path", "POST", {"param1": 123}, ["type of data", "is different"], 400),
            (
                "/test-api-path",
                "POST",
                {"param1": "any_format", "iterable_param": [{"name": "param1", "miss_param": "miss_param"}]},
                ["Miss required parameter"],
                400,
            ),
            (
                "/test-api-path",
                "POST",
                {"param1": "any_format", "iterable_param": [{"name": "param1", "value": 123}]},
                ["type of data", "is different"],
                400,
            ),
            ("/test-api-path", "POST", {"param1": "incorrect_format"}, ["format of data", "is incorrect"], 400),
            # Valid request with general format strategy
            ("/test-api-req-param-format", "GET", {"format_param_str": "string_value"}, None, 200),
            (
                "/test-api-req-param-format",
                "GET",
                {"format_param_str": "@\-_!#$%^&+*()\[\]<>?=/\\|`'\"}{~:;,."},
                None,
                200,
            ),
            ("/test-api-req-param-format", "GET", {"format_param_float": 123.123}, None, 200),
            (
                "/test-api-req-param-format",
                "GET",
                {"format_param_str": "string_value", "format_param_float": 123.123},
                None,
                200,
            ),
            # Valid request with enum format strategy
            ("/test-api-req-param-format", "POST", {"format_param": "ENUM2"}, None, 200),
            # Valid request with customize format strategy
            ("/test-api-req-param-format", "PUT", {"format_param": "123.123 USD\n456 TWD"}, None, 200),
            # Invalid request with general format strategy
            (
                "/test-api-req-param-format",
                "GET",
                {"format_param_str": "".join(["a" for _ in range(66)])},  # Too big size of string
                ["format should be", "str", "type data"],
                400,
            ),
            (
                "/test-api-req-param-format",
                "GET",
                {"format_param_float": "not big decimal value"},
                ["type of data", "is different"],
                400,
            ),
            (
                "/test-api-req-param-format",
                "GET",
                {"format_param_str": "string_value", "format_param_float": "not big decimal value"},
                ["type of data", "is different"],
                400,
            ),
            # Invalid request with enum format strategy
            (
                "/test-api-req-param-format",
                "POST",
                {"format_param": "NOT_EXIST_ENUM"},
                ["format should be", "oen of the enums value"],
                400,
            ),
            # Invalid request with customize format strategy
            (
                "/test-api-req-param-format",
                "PUT",
                {"format_param": "123.123 USD"},
                ["format should be", "like format as"],
                400,
            ),
            (
                "/test-api-req-param-format",
                "PUT",
                {"format_param": "not big decimal USD\n456 TWD"},
                ["format should be", "like format as"],
                400,
            ),
            (
                "/test-api-req-param-format",
                "PUT",
                {"format_param": "123.123 NOT_EXIST_CURRENCY\n456 TWD"},
                ["format should be", "like format as"],
                400,
            ),
        ],
    )
    def test_request_process(
        self,
        path: str,
        method: str,
        api_params: dict,
        error_msg_like: Optional[List[str]],
        expected_status_code: int,
        request_utils: BaseCurrentRequest,
        response_utils: BaseResponse,
        sut: Type[HTTPRequestProcess],
    ):
        # Mock request
        current_request = self._mock_request(path=path, method=method, api_params=api_params)

        request_utils.request_instance = MagicMock(return_value=current_request)  # type: ignore[method-assign]
        sut_instance = sut(
            request=request_utils,
            response=response_utils,
        )
        # Mock API attribute and function
        sut_instance._mock_api_details = {
            "/test-api-path": {
                _Google_Home_Value["http"]["request"]["method"]: MockAPI().deserialize(_Google_Home_Value),
                _Post_Google_Home_Value["http"]["request"]["method"]: MockAPI().deserialize(_Post_Google_Home_Value),
            },
            "/test-api-req-param-format": {
                _Test_Home_With_General_Format_Req_Param["http"]["request"]["method"]: MockAPI().deserialize(
                    _Test_Home_With_General_Format_Req_Param
                ),
                _Test_Home_With_Enums_Format_Req_Param["http"]["request"]["method"]: MockAPI().deserialize(
                    _Test_Home_With_Enums_Format_Req_Param
                ),
                _Test_Home_With_Customize_Format_Req_Param["http"]["request"]["method"]: MockAPI().deserialize(
                    _Test_Home_With_Customize_Format_Req_Param
                ),
            },
        }

        # Run target function
        response = self._run_request_process_func(sut_instance, request=current_request)

        # Verify
        response_content = self._get_response_content(response)
        response_str = response_content.decode("utf-8") if isinstance(response_content, bytes) else response_content
        logger.debug(f"response: {response_str}")
        assert isinstance(response, self._expected_response_type)
        assert response.status_code == expected_status_code
        if response.status_code != 200:
            regular = r""
            for er_msg_f in error_msg_like or []:
                regular += r".{0,512}" + re.escape(er_msg_f)
            assert re.search(regular, response_str, re.IGNORECASE)  # type: ignore[arg-type]

    @abstractmethod
    def _mock_request(self, path: str, method: str, api_params: dict) -> Mock:
        pass

    @abstractmethod
    def _run_request_process_func(self, sut: BaseHTTPProcess, **kwargs) -> Any:
        pass

    @abstractmethod
    def _get_response_content(self, response) -> Union[str, bytes, dict]:
        pass

    @property
    @abstractmethod
    def _expected_response_type(self) -> Type[Any]:
        pass


class TestHTTPRequestProcessWithFlask(HTTPProcessTestSpec):
    @pytest.fixture(scope="function")
    def request_utils(self) -> BaseCurrentRequest:
        return FlaskRequest()

    @pytest.fixture(scope="function")
    def response_utils(self) -> FlaskResponse:
        return FlaskResponse()

    @pytest.fixture(scope="function")
    def sut(self) -> Type[HTTPRequestProcess]:
        return HTTPRequestProcess

    @property
    def expected_sut_type(self) -> Type[Flask]:
        return Flask

    @property
    def mocker(self) -> MockerModule:
        return MockerModule(module_path="flask.Flask", return_value=FakeFlask("PyTest-Used"))

    def _mock_request(self, path: str, method: str, api_params: dict) -> Mock:
        def _get_list_param() -> str:
            has_single_iterable_param = api_params.get("single_iterable_param", None) is not None
            has_iterable_param = api_params.get("iterable_param", None) is not None
            if has_single_iterable_param:
                return "single_iterable_param"
            if has_iterable_param:
                return "iterable_param"
            return "just_mock"  # Doesn't have iterable parameter, so mock it as empty list.

        class DummyDict(dict):
            def getlist(self):
                pass

        dd = DummyDict()
        dd.update(**api_params)

        request = Mock()
        request.path = path
        request.method = method
        if method.upper() == "GET":
            request.args = dd
            request.args.getlist = MagicMock(return_value=api_params.get(_get_list_param(), []))  # type: ignore[method-assign]
        else:
            request.form = None
            request.data = dd
        return request

    def _run_request_process_func(self, sut: HTTPRequestProcess, **kwargs) -> "flask.Response":  # type: ignore[name-defined,override]
        return sut.process()

    def _get_response_content(self, response: "flask.Response") -> Union[str, bytes, dict]:  # type: ignore[name-defined]
        return response.data or response.json

    @property
    def _expected_response_type(self) -> Type[LibFlaskResponse]:
        return LibFlaskResponse


class TestHTTPRequestWithFastAPI(HTTPProcessTestSpec):
    @pytest.fixture(scope="function")
    def request_utils(self) -> FastAPIRequest:
        return FastAPIRequest()

    @pytest.fixture(scope="function")
    def response_utils(self) -> FastAPIResponse:
        return FastAPIResponse()

    @pytest.fixture(scope="function")
    def sut(self) -> Type[HTTPRequestProcess]:
        return HTTPRequestProcess

    @property
    def expected_sut_type(self) -> Type[FastAPI]:
        return FastAPI

    @property
    def mocker(self) -> MockerModule:
        return MockerModule(module_path="fastapi.FastAPI", return_value=FakeFastAPI())

    def _mock_request(self, path: str, method: str, api_params: dict) -> Mock:
        route_prop = Mock()
        route_prop.path = path

        request = Mock()
        request.scope = {
            "root_path": "",
            "route": route_prop,
        }

        request.method = method

        # Just for testing, source code won't have any usage like this
        request.api_parameters = api_params
        return request

    def _run_request_process_func(self, sut: HTTPRequestProcess, **kwargs) -> "fastapi.Response":  # type: ignore[override]
        class DummyModel:
            pass

        model = DummyModel()
        for k, v in cast(dict, kwargs["request"].api_parameters).items():
            setattr(model, k, v)
        return sut.process(model=model, request=kwargs["request"])

    def _get_response_content(self, response: "fastapi.Response") -> Union[str, bytes, dict]:
        return response.body

    @property
    def _expected_response_type(self) -> Type[LibFastAPIResponse]:
        return LibFastAPIResponse
