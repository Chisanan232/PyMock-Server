from pymock_api._utils.converter import _Convert
from pymock_api.model.api_config import (
    HTTP,
    BaseConfig,
    HTTPRequest,
    HTTPResponse,
    MockAPI,
    MockAPIs,
)

from ..._values import _Mocked_APIs


class TestInnerConvert:
    def test_mock_apis(self):
        # Run target function
        mocked_apis = _Convert.mock_apis(data=_Mocked_APIs)

        assertion_msg = "The value should be same as the value for testing."

        # Verify result
        assert isinstance(mocked_apis, MockAPIs), "It should be *MockAPIs* type instance."

        # Verify result --- BaseConfig
        assert isinstance(mocked_apis.base, BaseConfig), "It should be *BaseConfig* type instance."
        assert mocked_apis.base.url == _Mocked_APIs["base"]["url"], assertion_msg

        # Verify result --- APIs
        assert isinstance(mocked_apis.apis, dict), "It should be dict type object."
        mocked_apis_keys = list(_Mocked_APIs.keys())
        mocked_apis_keys.pop(0)
        assert (
            list(mocked_apis.apis.keys()) == mocked_apis_keys
        ), "The keys about every mocked API's name should be the same."

        for api_name, api_config in mocked_apis.apis.items():
            # For one mocked API --- entire object
            assert api_name in mocked_apis_keys, "The mocked API's name should be same as the value for test."
            assert isinstance(api_config, MockAPI), "It should be *MockAPI* type instance."
            assert api_config.url == _Mocked_APIs[api_name]["url"], assertion_msg

            # For one mocked API --- HTTP
            assert isinstance(api_config.http, HTTP), "It should be *HTTP* type instance."

            # For one mocked API --- HTTP request
            assert isinstance(api_config.http.request, HTTPRequest), "It should be *HTTPRequest* type instance."
            assert api_config.http.request.method == _Mocked_APIs[api_name]["http"]["request"]["method"], assertion_msg
            assert (
                api_config.http.request.parameters == _Mocked_APIs[api_name]["http"]["request"]["parameters"]
            ), assertion_msg

            # For one mocked API --- HTTP response
            assert isinstance(api_config.http.response, HTTPResponse), "It should be *HTTPResponse* type instance."
            assert api_config.http.response.value == _Mocked_APIs[api_name]["http"]["response"]["value"], assertion_msg
