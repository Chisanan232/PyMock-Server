import re
from abc import ABCMeta, abstractmethod
from test._values import (
    _Base_URL,
    _Mock_Template_Apply_Has_Tag_Setting,
    _Mock_Template_Apply_Scan_Strategy,
    _Test_API_Parameter,
    _Test_HTTP_Resp,
    _Test_Tag,
    _Test_URL,
    _TestConfig,
)
from typing import Any, Dict, List, Optional
from unittest.mock import Mock

import pytest

from pymock_api.model import (
    HTTP,
    APIParameter,
    HTTPRequest,
    HTTPResponse,
    MockAPI,
    MockAPIs,
)
from pymock_api.model.api_config import BaseConfig, TemplateConfig, _Config
from pymock_api.model.api_config.apis import ResponseProperty
from pymock_api.model.api_config.template import (
    TemplateAPI,
    TemplateApply,
    TemplateRequest,
    TemplateResponse,
    TemplateValues,
)
from pymock_api.model.enums import ResponseStrategy

_assertion_msg = "Its property's value should be same as we set."
MOCK_RETURN_VALUE: Mock = Mock()


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (None, None),
        ({}, {}),
        ({"any_key": "any_value"}, {"any_key": "any_value", "flag": "has run *test_function*"}),
    ],
)
def test_ensure_process_with_not_empty_value(data: Optional[Dict[str, str]], expected: Optional[Dict[str, str]]):
    class FakeObject:
        @_Config._ensure_process_with_not_empty_value
        def test_function(self, data: Dict[str, Any]) -> Any:
            data["flag"] = "has run *test_function*"
            return data

    fo = FakeObject()
    assert fo.test_function(data=data) == expected


def test_config_get_prop():
    class FakeConfig(_Config):
        def _compare(self, other: "_Config") -> bool:
            pass

        def serialize(self, data: Optional["_Config"] = None) -> Optional[Dict[str, Any]]:
            pass

        def deserialize(self, data: Dict[str, Any]) -> Optional["_Config"]:
            pass

    class Dummy:
        pass

    with pytest.raises(AttributeError) as exc_info:
        FakeConfig()._get_prop(data=Dummy(), prop="not_exist_prop")
    assert re.search(r"Cannot find attribute", str(exc_info.value), re.IGNORECASE)


class MockModel:
    @property
    def mock_apis(self) -> MockAPIs:
        return MockAPIs(template=self.template_config, base=self.base_config, apis=self.mock_api)

    @property
    def template_values_api(self) -> TemplateAPI:
        return TemplateAPI()

    @property
    def template_values_request(self) -> TemplateRequest:
        return TemplateRequest()

    @property
    def template_values_response(self) -> TemplateResponse:
        return TemplateResponse()

    @property
    def template_values(self) -> TemplateValues:
        return TemplateValues(
            api=self.template_values_api, request=self.template_values_request, response=self.template_values_response
        )

    @property
    def template_apply(self) -> TemplateApply:
        return TemplateApply(
            scan_strategy=_Mock_Template_Apply_Scan_Strategy,
            api=_Mock_Template_Apply_Has_Tag_Setting["api"],
        )

    @property
    def template_config(self) -> TemplateConfig:
        return TemplateConfig(values=self.template_values, apply=self.template_apply)

    @property
    def base_config(self) -> BaseConfig:
        return BaseConfig(url=_Base_URL)

    @property
    def mock_api(self) -> Dict[str, MockAPI]:
        return {"test_config": MockAPI(url=_Test_URL, http=self.http, tag=_Test_Tag)}

    @property
    def http(self) -> HTTP:
        return HTTP(request=self.http_request, response=self.http_response)

    @property
    def http_request(self) -> HTTPRequest:
        return HTTPRequest(method=_TestConfig.Request.get("method"), parameters=[self.api_parameter])

    @property
    def api_parameter(self) -> APIParameter:
        return APIParameter(
            name=_Test_API_Parameter["name"],
            required=_Test_API_Parameter["required"],
            default=_Test_API_Parameter["default"],
            value_type=_Test_API_Parameter["type"],
            value_format=_Test_API_Parameter["format"],
        )

    @property
    def http_response(self) -> HTTPResponse:
        return HTTPResponse(strategy=ResponseStrategy.STRING, value=_Test_HTTP_Resp)

    @property
    def response_properties(self) -> List[ResponseProperty]:
        prop_id = ResponseProperty(
            name="id",
            required=True,
            value_type="int",
        )
        prop_name = ResponseProperty(
            name="name",
            required=True,
            value_type="str",
        )
        return [prop_id, prop_name]


MOCK_MODEL = MockModel()


class ConfigTestSpec(metaclass=ABCMeta):
    _Mock_Model = MockModel()

    @pytest.fixture(scope="function")
    @abstractmethod
    def sut(self) -> _Config:
        pass

    @pytest.fixture(scope="function")
    @abstractmethod
    def sut_with_nothing(self) -> _Config:
        pass

    def test_eq_operation_with_valid_object(self, sut: _Config, sut_with_nothing: _Config):
        assert sut != sut_with_nothing

    def test_eq_operation_with_invalid_object(self, sut: _Config):
        with pytest.raises(TypeError) as exc_info:
            sut == "Invalid object"
        assert re.search(r"data types is different", str(exc_info), re.IGNORECASE)

    @abstractmethod
    def test_value_attributes(self, sut: _Config):
        pass

    def test_serialize(self, sut: _Config):
        assert sut.serialize() == self._expected_serialize_value()

    @abstractmethod
    def _expected_serialize_value(self) -> Any:
        pass

    def test_serialize_with_none(self, sut_with_nothing: _Config):
        assert sut_with_nothing.serialize() is None

    def test_deserialize(self, sut_with_nothing: _Config):
        obj = sut_with_nothing.deserialize(data=self._expected_serialize_value())
        self._expected_deserialize_value(obj)

    @abstractmethod
    def _expected_deserialize_value(self, obj: _Config) -> None:
        pass

    def test_deserialize_with_invalid_data(self, sut_with_nothing: _Config):
        assert sut_with_nothing.deserialize(data={}) == {}
