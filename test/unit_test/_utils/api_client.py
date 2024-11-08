from abc import ABCMeta, abstractmethod
from typing import Any
from unittest.mock import Mock, patch

import pytest
from urllib3 import HTTPResponse, PoolManager

from pymock_server._utils.api_client import BaseAPIClient, URLLibHTTPClient

from ._test_case import APIClientRequestTestCaseFactory

APIClientRequestTestCaseFactory.load()
API_CLIENT_REQUEST_TEST_CASE = APIClientRequestTestCaseFactory.get_test_case()


class APIClientTestSuite(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def client(self) -> BaseAPIClient:
        pass

    @pytest.mark.parametrize("api_doc_config_response_path", API_CLIENT_REQUEST_TEST_CASE)
    def test_request(self, api_doc_config_response_path: str, client: BaseAPIClient):
        with self._mock_request_process() as mock_request:
            mock_request.return_value = self._mock_return_value(api_doc_config_response_path)
            result = client.request(**self._request_params)
            self._verify(mock_request, result)

    @abstractmethod
    def _mock_request_process(self) -> patch.object:
        pass

    @abstractmethod
    def _mock_return_value(self, api_doc_config_response_path: str) -> Any:
        pass

    @property
    @abstractmethod
    def _request_params(self) -> dict:
        pass

    @abstractmethod
    def _verify(self, mock_request: Mock, result: Any) -> None:
        pass


class TestURLLibClient(APIClientTestSuite):
    @pytest.fixture(scope="function")
    def client(self) -> URLLibHTTPClient:
        return URLLibHTTPClient()

    def _mock_request_process(self) -> patch.object:
        return patch.object(PoolManager, "request")

    def _mock_return_value(self, api_doc_config_response_path: str) -> Any:
        with open(api_doc_config_response_path, "r", encoding="utf-8") as file_stream:
            return HTTPResponse(body=bytes(file_stream.read(), "utf-8"))

    @property
    def _request_params(self) -> dict:
        return {
            "method": "GET",
            "url": "Swagger API document URL",
        }

    def _verify(self, mock_request: Mock, result: Any) -> None:
        mock_request.assert_called_once_with(method="GET", url="Swagger API document URL")
        assert not isinstance(result, HTTPResponse)
        assert isinstance(result, dict)
