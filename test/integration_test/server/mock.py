import json
from abc import ABCMeta, abstractmethod

import pytest

from pymock_api._utils import load_config
from pymock_api.model.api_config import APIConfig
from pymock_api.server.application import FlaskServer
from pymock_api.server.mock import MockHTTPServer, _HTTPResponse


class MockHTTPServerTestSpec(metaclass=ABCMeta):
    @pytest.fixture(scope="class")
    @abstractmethod
    def server_app_type(self) -> FlaskServer:
        pass

    @pytest.fixture(scope="function")
    def mock_server_app(self, server_app_type: FlaskServer):
        return MockHTTPServer(config_path=self.file_path, app_server=server_app_type, auto_setup=True).web_app

    @pytest.fixture(scope="function")
    @abstractmethod
    def client(self, mock_server_app):
        return mock_server_app.test_client()

    @pytest.fixture(scope="session")
    def api_config(self) -> APIConfig:
        return load_config(self.file_path)

    @property
    def file_path(self) -> str:
        return "./api.yaml"


class TestMockHTTPServerWithFlaskApp(MockHTTPServerTestSpec):
    @pytest.fixture(scope="class")
    def server_app_type(self) -> FlaskServer:
        return FlaskServer()

    @pytest.fixture(scope="function")
    def client(self, mock_server_app):
        return mock_server_app.test_client()

    def test_mock_apis(self, client, api_config: APIConfig):
        for one_api_name, one_api_config in api_config.apis.apis.items():
            # Send HTTP request to target API and get its response data
            http_req_with_method = getattr(client, one_api_config.http.request.method.lower())
            response = http_req_with_method(api_config.apis.base.url + one_api_config.url)
            response_str = response.data.decode("utf-8")
            try:
                under_test_http_resp = json.loads(response_str)
            except:
                under_test_http_resp = response_str

            # Get the expected result data
            expected_http_resp = _HTTPResponse.generate(data=one_api_config.http.response.value)

            # Verify the result data
            assert (
                under_test_http_resp == expected_http_resp
            ), f"The response data should be the same at mocked API '{one_api_name}'."
