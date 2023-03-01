from typing import Any, Dict

from pymock_api._utils.converter import Convert
from pymock_api.model.api_config import (
    HTTP,
    APIConfig,
    BaseConfig,
    HTTPRequest,
    HTTPResponse,
    MockAPI,
    MockAPIs,
)

from ..._values import _Mocked_APIs, _Test_Config_Value


class TestConvert:
    @property
    def test_config(self) -> Dict[str, Any]:
        return _Test_Config_Value

    def test_api_config(self):
        api_config = Convert.api_config(data=self.test_config)

        # Verify result
        assert isinstance(api_config, APIConfig), "It should be *APIConfig* type instance."
        assert len(api_config) == len(
            api_config.apis
        ), "The length of *APIConfig* should be same as the length of property *APIConfig.apis*."
        assert api_config.has_apis() is True, "It should be *True* because of non-empty data."

        # Verify the details
        assert (
            api_config.name == _Test_Config_Value["name"]
        ), "The property *name* should be same as the value for testing."
        assert (
            api_config.description == _Test_Config_Value["description"]
        ), "The property *description* should be same as the value for testing."
        assert isinstance(api_config.apis, MockAPIs), "It should be *MockAPIs* type instance."
        assert isinstance(api_config.apis.base, BaseConfig), "It should be *BaseConfig* type instance."
        assert isinstance(api_config.apis.apis, dict), "It should be dict type object."
        keys = list(_Mocked_APIs.keys())
        keys.pop(0)
        assert list(api_config.apis.apis.keys()) == keys, "The keys about every mocked API's name should be the same."

        assertion_msg = "The value should be same as the value for testing."
        for test_name, criteria_name in zip(api_config.apis.apis.keys(), keys):
            assert api_config.apis.apis[test_name].url == _Mocked_APIs[criteria_name]["url"], assertion_msg

            assert isinstance(api_config.apis.apis[test_name], MockAPI), "It should be *MockAPI* type instance."
            assert isinstance(api_config.apis.apis[test_name].http, HTTP), "It should be *HTTP* type instance."

            assert isinstance(
                api_config.apis.apis[test_name].http.request, HTTPRequest
            ), "It should be *HTTPRequest* type instance."
            assert (
                api_config.apis.apis[test_name].http.request.method
                == _Mocked_APIs[criteria_name]["http"]["request"]["method"]
            ), assertion_msg
            assert (
                api_config.apis.apis[test_name].http.request.parameters
                == _Mocked_APIs[criteria_name]["http"]["request"]["parameters"]
            ), assertion_msg

            assert isinstance(
                api_config.apis.apis[test_name].http.response, HTTPResponse
            ), "It should be *HTTPResponse* type instance."
            assert (
                api_config.apis.apis[test_name].http.response.value
                == _Mocked_APIs[criteria_name]["http"]["response"]["value"]
            ), assertion_msg
