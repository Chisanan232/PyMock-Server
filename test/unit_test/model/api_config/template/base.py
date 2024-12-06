import copy
from abc import ABCMeta, abstractmethod
from typing import TypeVar

import pytest

from pymock_server import APIConfig
from pymock_server.model import (
    HTTP,
    APIParameter,
    HTTPRequest,
    HTTPResponse,
    MockAPI,
    TemplateConfig,
)
from pymock_server.model.api_config import ResponseProperty
from pymock_server.model.api_config.template import _BaseTemplateAccessable

# isort: off
from test._values import _Mock_Template_Setting, _Test_Config_Value

# isort: on

_BaseTemplateAccessableType = TypeVar("_BaseTemplateAccessableType", bound=_BaseTemplateAccessable)


class BaseAccessTemplateConfigTestSuite(metaclass=ABCMeta):

    @pytest.fixture(scope="module")
    def entire_mock_api_config(self) -> APIConfig:
        return APIConfig().deserialize(_Test_Config_Value)

    def test_template_config_access(self, entire_mock_api_config: APIConfig):
        assert self.under_test_config(entire_mock_api_config) == self.expect_template_config

    def test_template_config_not_same_after_modify(self, entire_mock_api_config: APIConfig):
        template_config = copy.copy(self.expect_template_config)
        template_config.common_config.format.variables = []
        assert self.under_test_config(entire_mock_api_config) != template_config

    @property
    def expect_template_config(self) -> TemplateConfig:
        return TemplateConfig().deserialize(_Mock_Template_Setting)

    @abstractmethod
    def under_test_config(self, entire_mock_api_config: APIConfig) -> TemplateConfig:
        pass


class TestAPIConfigAccessTemplateConfig(BaseAccessTemplateConfigTestSuite):

    def under_test_config(self, entire_mock_api_config: APIConfig) -> TemplateConfig:
        return entire_mock_api_config.apis.template


class TestMockAPIAccessTemplateConfig(BaseAccessTemplateConfigTestSuite):

    @property
    def _under_test_api_key(self) -> str:
        return "google_home"

    def get_template_accessable_config(self, entire_mock_api_config: APIConfig) -> MockAPI:
        one_mock_api = entire_mock_api_config.apis.apis[self._under_test_api_key]
        assert isinstance(one_mock_api, MockAPI)
        return one_mock_api

    def under_test_config(self, entire_mock_api_config: APIConfig) -> TemplateConfig:
        return self.get_template_accessable_config(entire_mock_api_config)._current_template


class TestHTTPAccessTemplateConfig(TestMockAPIAccessTemplateConfig):

    def get_template_accessable_config(self, entire_mock_api_config: APIConfig) -> HTTP:
        one_mock_api: MockAPI = super().get_template_accessable_config(entire_mock_api_config)
        assert one_mock_api.http
        assert isinstance(one_mock_api.http, HTTP)
        return one_mock_api.http


class TestHTTPRequestAccessTemplateConfig(TestHTTPAccessTemplateConfig):

    def get_template_accessable_config(self, entire_mock_api_config: APIConfig) -> HTTPRequest:
        one_mock_api_http: HTTP = super().get_template_accessable_config(entire_mock_api_config)
        assert one_mock_api_http.request
        assert isinstance(one_mock_api_http.request, HTTPRequest)
        return one_mock_api_http.request


class TestHTTPRequestAPIParameterAccessTemplateConfig(TestHTTPRequestAccessTemplateConfig):

    def get_template_accessable_config(self, entire_mock_api_config: APIConfig) -> APIParameter:
        one_mock_api_http_req: HTTPRequest = super().get_template_accessable_config(entire_mock_api_config)
        assert one_mock_api_http_req.parameters
        assert isinstance(one_mock_api_http_req.parameters[0], APIParameter)
        return one_mock_api_http_req.parameters[0]


class TestHTTPResponseAccessTemplateConfig(TestHTTPAccessTemplateConfig):

    def get_template_accessable_config(self, entire_mock_api_config: APIConfig) -> HTTPResponse:
        one_mock_api_http: HTTP = super().get_template_accessable_config(entire_mock_api_config)
        assert one_mock_api_http.response
        assert isinstance(one_mock_api_http.response, HTTPResponse)
        return one_mock_api_http.response


class TestHTTPResponsePropertyAccessTemplateConfig(TestHTTPResponseAccessTemplateConfig):
    @property
    def _under_test_api_key(self) -> str:
        return "foo-object"

    def get_template_accessable_config(self, entire_mock_api_config: APIConfig) -> ResponseProperty:
        one_mock_api_http_resp: HTTPResponse = super().get_template_accessable_config(entire_mock_api_config)
        assert one_mock_api_http_resp.properties
        assert isinstance(one_mock_api_http_resp.properties[0], ResponseProperty)
        return one_mock_api_http_resp.properties[0]
