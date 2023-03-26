import json
from abc import abstractmethod
from typing import Union

import fastapi
import flask
import pytest
from fastapi.testclient import TestClient as FastAPITestClient
from flask.app import Response as FlaskResponse
from httpx import Response as FastAPIResponse

from pymock_api._utils import load_config
from pymock_api.model.api_config import APIConfig
from pymock_api.server.application import (
    BaseAppServer,
    FastAPIServer,
    FlaskServer,
    _HTTPResponse,
)

from ..._values import _YouTube_API_Content
from .._spec import ConfigFile, MockAPI_Config_Path, file


class MockHTTPServerTestSpec:
    config_file: ConfigFile = ConfigFile()

    @pytest.fixture(scope="class")
    @abstractmethod
    def server_app_type(self) -> BaseAppServer:
        pass

    @pytest.fixture(scope="class", autouse=True)
    def api_config(self) -> APIConfig:
        # Ensure that it doesn't have file
        self.config_file.delete()
        # Create the target file before run test
        self.config_file.generate()
        # Create the example extended file for one of mocked APIs
        file.write(path="youtube.json", content=_YouTube_API_Content, serialize=lambda content: json.dumps(content))

        yield load_config(MockAPI_Config_Path)

        # Delete file finally
        self.config_file.delete()
        file.delete("youtube.json")

    @pytest.fixture(scope="class")
    def mock_server_app(
        self, server_app_type: BaseAppServer, api_config: APIConfig
    ) -> Union[flask.Flask, fastapi.FastAPI]:
        server_app_type.create_api(mocked_apis=api_config.apis)
        return server_app_type.web_application

    @pytest.fixture(scope="function")
    @abstractmethod
    def client(
        self, mock_server_app: Union[flask.Flask, fastapi.FastAPI]
    ) -> Union["flask.testing.FlaskClient", FastAPITestClient]:
        pass

    def test_mock_apis(self, client: Union["flask.testing.FlaskClient", FastAPITestClient], api_config: APIConfig):
        for one_api_name, one_api_config in api_config.apis.apis.items():
            # Send HTTP request to target API and get its response data
            response = getattr(client, one_api_config.http.request.method.lower())(
                api_config.apis.base.url + one_api_config.url
            )
            under_test_http_resp = self._deserialize_response(response)

            # Get the expected result data
            expected_http_resp = _HTTPResponse.generate(data=one_api_config.http.response.value)

            # Verify the result data
            assert (
                under_test_http_resp == expected_http_resp
            ), f"The response data should be the same at mocked API '{one_api_name}'."

    @abstractmethod
    def _deserialize_response(self, response: Union[FlaskResponse, FastAPIResponse]) -> Union[str, dict]:
        pass


class TestMockHTTPServerWithFlaskApp(MockHTTPServerTestSpec):
    @pytest.fixture(scope="class")
    def server_app_type(self) -> FlaskServer:
        return FlaskServer()

    @pytest.fixture(scope="function")
    def client(self, mock_server_app: flask.Flask) -> "flask.testing.FlaskClient":
        return mock_server_app.test_client()

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

    def _deserialize_response(self, response: FastAPIResponse) -> Union[str, dict]:
        try:
            return response.json()
        except:
            return response.text
