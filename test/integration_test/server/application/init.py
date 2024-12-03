import json
from abc import abstractmethod
from typing import Any, Union

import fastapi
import flask
import pytest
from fastapi.testclient import TestClient as FastAPITestClient
from flask.app import Response as FlaskResponse
from httpx import Response as FastAPIResponse

from pymock_server import APIConfig
from pymock_server.model import MockAPI, load_config
from pymock_server.model.api_config.apis import APIParameter
from pymock_server.server.application import BaseAppServer, FastAPIServer, FlaskServer
from pymock_server.server.application.response import HTTPResponse as _HTTPResponse

from ...._file_utils import MockAPI_Config_Yaml_Path, file, yaml_factory
from ...._values import (
    _Base_URL,
    _Delete_Google_Home_Value,
    _Foo_Object_Data_Value,
    _Foo_Object_Value,
    _Foo_With_Multiple_Variables_In_Api,
    _Foo_With_Variable_In_Api,
    _Google_Home_Value,
    _Post_Google_Home_Value,
    _Put_Google_Home_Value,
    _Test_Home,
    _Test_Home_With_Customize_Format_Req_Param,
    _Test_Home_With_Enums_Format_Req_Param,
    _Test_Home_With_General_Format_Req_Param,
    _Test_Iterable_Parameter_With_MultiValue,
    _YouTube_API_Content,
    _YouTube_Home_Value,
)

WebLibraryType = Any  # flask.Flask, fastapi.FastAPI
ResponseType = Any  # FlaskResponse, FastAPIResponse


def _test_api_attr(api: dict, payload: dict) -> tuple:
    real_url = api["under_test_url"] if "under_test_url" in api.keys() else api["url"]
    return api["url"], f"{_Base_URL}{real_url}", f"{api['http']['request']['method']}", payload


class MockHTTPServerTestSpec:
    config_file: yaml_factory = yaml_factory()

    @pytest.fixture(scope="class")
    @abstractmethod
    def server_app_type(self) -> BaseAppServer:
        pass

    @pytest.fixture(scope="class", autouse=True)
    def api_config(self) -> APIConfig:  # type: ignore
        # Ensure that it doesn't have file
        self.config_file.delete()
        # Create the target file before run test
        self.config_file.generate()
        # Create the example extended file for one of mocked APIs
        file.write(path="youtube.json", content=_YouTube_API_Content, serialize=lambda content: json.dumps(content))

        yield load_config(MockAPI_Config_Yaml_Path)

        # Delete file finally
        self.config_file.delete()
        file.delete("youtube.json")

    @pytest.fixture(scope="class")
    def mock_server_app(
        self, server_app_type: BaseAppServer, api_config: APIConfig
    ) -> Union[flask.Flask, fastapi.FastAPI]:
        assert api_config.apis
        server_app_type.create_api(mocked_apis=api_config.apis)
        return server_app_type.web_application

    @pytest.fixture(scope="function")
    @abstractmethod
    def client(self, mock_server_app: WebLibraryType) -> Union["flask.testing.FlaskClient", FastAPITestClient]:
        pass

    @pytest.mark.parametrize(
        ("url", "real_url", "http_method", "payload"),
        [
            _test_api_attr(
                api=_Google_Home_Value,
                payload={
                    "param1": "any_format",
                    "single_iterable_param": ["param1", "param2", "param3"],
                },
            ),
            _test_api_attr(
                api=_Post_Google_Home_Value,
                payload={
                    "param1": "any_format",
                    "iterable_param": [
                        {"name": "param1", "value": "value1"},
                        {"name": "param2", "value": "value2"},
                        {"name": "param3", "value": "value3"},
                    ],
                },
            ),
            _test_api_attr(api=_Put_Google_Home_Value, payload={"param1": "any_format"}),
            _test_api_attr(api=_Delete_Google_Home_Value, payload={}),
            _test_api_attr(api=_Test_Home, payload={"param1": "any_format"}),
            _test_api_attr(api=_YouTube_Home_Value, payload={"param1": "any_format"}),
            _test_api_attr(api=_Foo_Object_Value, payload={"param1": "any_format"}),
            _test_api_attr(api=_Foo_Object_Data_Value, payload={"param1": "any_format"}),
            _test_api_attr(api=_Foo_With_Variable_In_Api, payload={"param1": "any_format"}),
            _test_api_attr(api=_Foo_With_Multiple_Variables_In_Api, payload={"param1": "any_format"}),
            _test_api_attr(
                api=_Test_Home_With_General_Format_Req_Param,
                payload={"format_param_str": "string_value_with_any_format"},
            ),
            _test_api_attr(
                api=_Test_Home_With_General_Format_Req_Param,
                payload={"format_param_float": 123.123},
            ),
            _test_api_attr(api=_Test_Home_With_Enums_Format_Req_Param, payload={"format_param": "ENUM2"}),
            _test_api_attr(
                api=_Test_Home_With_Customize_Format_Req_Param, payload={"format_param": "123.321 USD\n567 TWD"}
            ),
        ],
    )
    def test_mock_apis(
        self,
        url: str,
        real_url: str,
        http_method: str,
        payload: dict,
        client: Union["flask.testing.FlaskClient", FastAPITestClient],
        api_config: APIConfig,
    ):
        assert api_config.apis and api_config.apis.apis and api_config.apis.base
        one_api_configs = api_config.apis.get_all_api_config_by_url(url, base=api_config.apis.base)

        if http_method.upper() == "GET":
            request_params = self._client_get_req_func_params(one_api_configs[http_method.upper()], payload)
        else:
            if payload:
                request_params = {
                    "json": payload,
                    "headers": {"Content-Type": "application/json"},
                }
            else:
                request_params = {
                    "headers": {"Content-Type": "application/json"},
                }
        response = getattr(client, http_method.lower())(real_url, **request_params)
        under_test_http_resp = self._deserialize_response(response)

        # Get the expected result data
        config_response = one_api_configs[http_method.upper()].http.response  # type: ignore[union-attr]
        expected_http_resp = _HTTPResponse.generate(data=config_response)  # type: ignore[arg-type]

        # Verify the result data
        assert (
            under_test_http_resp == expected_http_resp
        ), f"The response data should be the same at mocked API '{one_api_configs[http_method.upper()]}'."

    def _client_non_get_req_func_params(self, one_api_config: MockAPI) -> dict:
        params = one_api_config.http.request.parameters  # type: ignore[union-attr]
        if params:
            if APIParameter().deserialize(data=_Test_Iterable_Parameter_With_MultiValue) in params:
                return {
                    "json": {
                        "param1": "any_format",
                        "iterable_param": [
                            {"name": "param1", "value": "value1"},
                            {"name": "param2", "value": "value2"},
                            {"name": "param3", "value": "value3"},
                        ],
                    },
                    "headers": {"Content-Type": "application/json"},
                }
            else:
                return {
                    "json": {"param1": "any_format"},
                    "headers": {"Content-Type": "application/json"},
                }
        else:
            if one_api_config.http.request.method.upper() == "DELETE":  # type: ignore[union-attr]
                return {
                    # "headers": {"Content-Type": "application/json"},
                }
            else:
                return {
                    "json": {},
                    "headers": {"Content-Type": "application/json"},
                }

    @abstractmethod
    def _client_get_req_func_params(self, one_api_config: MockAPI, payload: dict) -> dict:
        pass

    @abstractmethod
    def _deserialize_response(self, response: ResponseType) -> Union[str, dict]:
        pass


class TestMockHTTPServerWithFlaskApp(MockHTTPServerTestSpec):
    @pytest.fixture(scope="class")
    def server_app_type(self) -> FlaskServer:
        return FlaskServer()

    @pytest.fixture(scope="function")
    def client(self, mock_server_app: flask.Flask) -> "flask.testing.FlaskClient":
        return mock_server_app.test_client()

    def _client_get_req_func_params(self, one_api_config: MockAPI, payload: dict) -> dict:
        params = one_api_config.http.request.parameters  # type: ignore[union-attr]
        if params:
            if APIParameter().deserialize(data=_Test_Iterable_Parameter_With_MultiValue) in params:
                return {
                    "query_string": payload,
                    "headers": {"Content-Type": "application/json"},
                }
            else:
                return {
                    "query_string": payload,
                    "headers": {"Content-Type": "application/json"},
                }
        else:
            return {
                "query_string": {},
                "headers": {"Content-Type": "application/json"},
            }

    def _deserialize_response(self, response: FlaskResponse) -> Union[str, dict]:
        response_str = response.data.decode("utf-8")
        try:
            return json.loads(response_str)
        except:
            return response_str


class TestMockHTTPServerWithFastAPIApp(MockHTTPServerTestSpec):
    @pytest.fixture(scope="class")
    def server_app_type(self) -> FastAPIServer:
        return FastAPIServer()

    @pytest.fixture(scope="function")
    def client(self, mock_server_app: fastapi.FastAPI) -> FastAPITestClient:
        return FastAPITestClient(mock_server_app)

    def _client_get_req_func_params(self, one_api_config: MockAPI, payload: dict) -> dict:
        params = one_api_config.http.request.parameters  # type: ignore[union-attr]
        if params:
            if APIParameter().deserialize(data=_Test_Iterable_Parameter_With_MultiValue) in params:
                return {
                    "params": payload,
                    "headers": {"Content-Type": "application/json"},
                }
            else:
                return {
                    "params": payload,
                    "headers": {"Content-Type": "application/json"},
                }
        else:
            return {
                "params": {},
                "headers": {"Content-Type": "application/json"},
            }

    def _deserialize_response(self, response: FastAPIResponse) -> Union[str, dict]:
        try:
            return response.json()
        except:
            return response.text
