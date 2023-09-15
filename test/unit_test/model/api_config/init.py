import random
import re
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Type, Union
from unittest.mock import Mock, patch

import pytest

from pymock_api._utils import YAML
from pymock_api._utils.file_opt import JSON
from pymock_api.model.api_config import (
    HTTP,
    APIParameter,
    BaseConfig,
    HTTPRequest,
    HTTPResponse,
    IteratorItem,
    MockAPI,
    MockAPIs,
    ResponseProperty,
    TemplateAPI,
    TemplateApply,
    TemplateConfig,
    TemplateRequest,
    TemplateResponse,
    TemplateSetting,
    TemplateValues,
    _Config,
    _TemplatableConfig,
)
from pymock_api.model.enums import Format, ResponseStrategy

from ...._values import (
    _Base_URL,
    _Mock_Templatable_Setting,
    _Mock_Template_API_Request_Setting,
    _Mock_Template_API_Response_Setting,
    _Mock_Template_API_Setting,
    _Mock_Template_Apply_Has_Tag_Setting,
    _Mock_Template_Apply_Scan_Strategy,
    _Mock_Template_Setting,
    _Mock_Template_Values_Setting,
    _Test_API_Parameter,
    _Test_HTTP_Resp,
    _Test_Iterable_Parameter_Item_Name,
    _Test_Iterable_Parameter_Item_Value,
    _Test_Iterable_Parameter_Items,
    _Test_Iterable_Parameter_With_MultiValue,
    _Test_Response_Properties,
    _Test_Response_Property_List,
    _Test_Tag,
    _Test_URL,
    _TestConfig,
)
from ._base import (
    MOCK_MODEL,
    MOCK_RETURN_VALUE,
    ConfigTestSpec,
    MockModel,
    _assertion_msg,
)


class TemplatableConfigTestSuite(ConfigTestSpec, ABC):
    def test_apply_template_props_default_value(self, sut: _TemplatableConfig):
        assert sut.apply_template_props is True

    def test_apply_template_props_should_be_serialize_if_has_in_config(self, sut_with_nothing: _TemplatableConfig):
        # Given data
        has_prop_apply_template_props = self._expected_serialize_value().copy()
        has_prop_apply_template_props.update(_Mock_Templatable_Setting)

        # Run target function
        deserialized_sut = sut_with_nothing.deserialize(has_prop_apply_template_props)
        serialized_sut = deserialized_sut.serialize()

        # Verify
        assert serialized_sut.get("apply_template_props", None) is not None
        assert serialized_sut["apply_template_props"] is _Mock_Templatable_Setting["apply_template_props"]

    def test_apply_template_props_should_not_be_serialize_if_not_has_in_config(
        self, sut_with_nothing: _TemplatableConfig
    ):
        # Given data
        not_has_prop_apply_template_props = self._expected_serialize_value().copy()

        # Run target function
        deserialized_sut = sut_with_nothing.deserialize(not_has_prop_apply_template_props)
        serialized_sut = deserialized_sut.serialize()

        # Verify
        assert serialized_sut.get("apply_template_props", None) is None


class TestMockAPIs(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> MockAPIs:
        return MockAPIs(
            template=MOCK_MODEL.template_config, base=self._Mock_Model.base_config, apis=self._Mock_Model.mock_api
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> MockAPIs:
        return MockAPIs()

    def test___len__(self, sut: MockAPIs):
        assert len(sut) == len(
            self._Mock_Model.mock_api.keys()
        ), f"The size of *MockAPIs* data object should be same as object '{self._Mock_Model.mock_api}'."

    def test_value_attributes(self, sut: MockAPIs):
        assert sut.template == MOCK_MODEL.template_config, _assertion_msg
        assert sut.base == self._Mock_Model.base_config, _assertion_msg
        assert sut.apis == self._Mock_Model.mock_api, _assertion_msg

    @pytest.mark.parametrize(
        ("setting_val", "should_call_deserialize"),
        [
            ({}, False),
            ({"test": "test"}, True),
            (TemplateConfig(), False),
        ],
    )
    @patch.object(TemplateConfig, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_template_with_valid_obj(
        self,
        mock_deserialize: Mock,
        setting_val: Union[dict, TemplateConfig],
        should_call_deserialize: bool,
        sut_with_nothing: MockAPIs,
    ):
        # Run target function
        sut_with_nothing.template = setting_val
        # Verify the running result
        if should_call_deserialize:
            mock_deserialize.assert_called_once_with(data=setting_val)
            assert sut_with_nothing.template == MOCK_RETURN_VALUE
        else:
            mock_deserialize.assert_not_called()
            assert sut_with_nothing.template == TemplateConfig()

    @patch.object(TemplateConfig, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_template_with_invalid_obj(self, mock_deserialize: Mock, sut_with_nothing: MockAPIs):
        with pytest.raises(TypeError) as exc_info:
            sut_with_nothing.template = "Invalid object"
        mock_deserialize.assert_not_called()
        assert re.search(r"Setter .{1,32} only accepts .{1,32} type object.", str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize(
        ("setting_val", "should_call_deserialize"),
        [
            ({}, False),
            ({"test": "test"}, True),
            (Mock(BaseConfig()), False),
        ],
    )
    @patch.object(BaseConfig, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_base_with_valid_obj(
        self,
        mock_deserialize: Mock,
        setting_val: Union[dict, BaseConfig],
        should_call_deserialize: bool,
        sut_with_nothing: MockAPIs,
    ):
        # Run target function
        sut_with_nothing.base = setting_val
        # Verify the running result
        if should_call_deserialize:
            mock_deserialize.assert_called_once_with(data=setting_val)
            assert sut_with_nothing.base == MOCK_RETURN_VALUE
        else:
            mock_deserialize.assert_not_called()
            assert sut_with_nothing.base == (setting_val if setting_val else None)

    @patch.object(BaseConfig, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_base_with_invalid_obj(self, mock_deserialize: Mock, sut_with_nothing: MockAPIs):
        with pytest.raises(TypeError) as exc_info:
            sut_with_nothing.base = "Invalid object"
        mock_deserialize.assert_not_called()
        assert re.search(r"Setter .{1,32} only accepts .{1,32} type object.", str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize(
        ("setting_val", "should_call_deserialize"),
        [
            ({}, False),
            ({"test": "test"}, True),
            ({"test": Mock(MockAPI())}, False),
        ],
    )
    @patch.object(MockAPI, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_apis_with_valid_obj(
        self,
        mock_deserialize: Mock,
        setting_val: Union[dict, BaseConfig],
        should_call_deserialize: bool,
        sut_with_nothing: MockAPIs,
    ):
        # Run target function
        sut_with_nothing.apis = setting_val
        # Verify the running result
        if should_call_deserialize:
            expected_apis = {}
            for api_name, api_value in setting_val.items():
                mock_deserialize.assert_called_once_with(data=api_value)
                expected_apis[api_name] = MOCK_RETURN_VALUE
                assert sut_with_nothing.apis[api_name] == MOCK_RETURN_VALUE
            assert sut_with_nothing.apis == expected_apis
        else:
            mock_deserialize.assert_not_called()
            assert sut_with_nothing.apis == setting_val

    @pytest.mark.parametrize(
        ("setting_val", "expected_err", "err_msg_regex"),
        [
            ("Invalid object", TypeError, r"Setter .{1,32} only accepts .{1,32} type object."),
            ({"t1": "test", "t2": Mock(MockAPI())}, ValueError, r".{1,32} multiple types .{1,64} unify .{1,32} type"),
        ],
    )
    @patch.object(MockAPI, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_apis_with_invalid_obj(
        self,
        mock_deserialize: Mock,
        setting_val: Union[str, dict],
        expected_err: Exception,
        err_msg_regex,
        sut_with_nothing: MockAPIs,
    ):
        with pytest.raises(expected_err) as exc_info:
            sut_with_nothing.apis = setting_val
        mock_deserialize.assert_not_called()
        assert re.search(err_msg_regex, str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize(
        "test_data",
        [
            {"template": "template_setting", "base": "base_info"},
            {"template": "template_setting", "base": "base_info", "apis": {"api_name": "api_info"}},
        ],
    )
    @patch.object(MockAPI, "deserialize", return_value=None)
    @patch.object(BaseConfig, "deserialize", return_value=None)
    @patch.object(TemplateConfig, "deserialize", return_value=None)
    def test_deserialize_with_nonideal_value(
        self,
        mock_deserialize_template: Mock,
        mock_deserialize_base: Mock,
        mock_deserialize_mock_api: Mock,
        test_data: dict,
        sut_with_nothing: MockAPIs,
    ):
        assert sut_with_nothing.deserialize(data=test_data) is not None
        mock_deserialize_template.assert_called_once_with(data="template_setting")
        mock_deserialize_base.assert_called_once_with(data="base_info")
        if len(test_data.keys()) > 2:
            mock_deserialize_mock_api.assert_called_once_with(data="api_info")
        else:
            mock_deserialize_mock_api.assert_not_called()

    def _expected_serialize_value(self) -> Any:
        return _TestConfig.Mock_APIs

    def _expected_deserialize_value(self, obj: MockAPIs) -> None:
        assert isinstance(obj, MockAPIs)
        assert obj.base.url == _Base_URL
        assert obj.apis == self._Mock_Model.mock_api

    def test_get_api_config_by_url(self, sut: MockAPIs):
        api_config = sut.get_api_config_by_url(url=_Test_URL)
        assert api_config.url == _Test_URL
        assert api_config.http.request.method == _TestConfig.Request.get("method")
        assert api_config.http.request.parameters == [self._Mock_Model.api_parameter]
        assert api_config.http.response.value == _Test_HTTP_Resp

    def test_fail_get_api_config_by_url(self, sut: MockAPIs):
        api_config = sut.get_api_config_by_url(url="Not exist this path's API config")
        assert api_config is None

    def test_group_by_url(self, sut_with_nothing: MockAPIs):
        foo_get_api = MockAPI(url="/foo")
        foo_get_api.set_request(method="GET")

        foo_post_api = MockAPI(url="/foo")
        foo_post_api.set_request(method="POST")

        foo_boo_api = MockAPI(url="/foo-boo")
        foo_boo_api.set_request(method="GET")

        sut_with_nothing.apis = {
            "get_foo": foo_get_api,
            "post_foo": foo_post_api,
            "get_foo_boo": foo_boo_api,
        }

        aggregated_apis = sut_with_nothing.group_by_url()

        assert len(aggregated_apis.keys()) == 2

        assert "/foo" in aggregated_apis.keys() and "/foo-boo" in aggregated_apis.keys()
        for val in aggregated_apis.values():
            assert isinstance(val, list)
            assert False not in list(map(lambda a: isinstance(a, MockAPI), val))

        assert len(aggregated_apis["/foo"]) == 2
        assert len(aggregated_apis["/foo-boo"]) == 1

        assert [a.http.request.method for a in aggregated_apis["/foo"]] == [
            foo_get_api.http.request.method,
            foo_post_api.http.request.method,
        ]
        assert [a.http.request.method for a in aggregated_apis["/foo-boo"]] == [foo_boo_api.http.request.method]


class TestBaseConfig(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> BaseConfig:
        return BaseConfig(url=_Base_URL)

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> BaseConfig:
        return BaseConfig()

    def test_value_attributes(self, sut: BaseConfig):
        assert sut.url == _Base_URL, _assertion_msg

    def _expected_serialize_value(self) -> dict:
        return _TestConfig.Base

    def _expected_deserialize_value(self, obj: BaseConfig) -> None:
        assert isinstance(obj, BaseConfig)
        assert obj.url == _Base_URL


class TemplateSettingTestSuite(ConfigTestSpec, ABC):
    @property
    @abstractmethod
    def under_test_data(self) -> dict:
        pass

    @property
    @abstractmethod
    def sut_object(self) -> Type[TemplateSetting]:
        pass

    @pytest.fixture(scope="function")
    def sut(self) -> TemplateSetting:
        args = {
            "base_file_path": self.under_test_data["base_file_path"],
            "config_path": self.under_test_data["config_path"],
            "config_path_format": self.under_test_data["config_path_format"],
        }
        return self.sut_object(**args)

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> TemplateSetting:
        return self.sut_object()

    def test_eq_operation_with_valid_object(self, sut: TemplateSetting, sut_with_nothing: TemplateSetting):
        sut.base_file_path = "./tmp"
        super().test_eq_operation_with_valid_object(sut, sut_with_nothing)

    def test_serialize_with_none(self, sut_with_nothing: TemplateSetting):
        assert sut_with_nothing.serialize() is not None
        assert sut_with_nothing.base_file_path == "./"
        assert sut_with_nothing.config_path == ""
        assert sut_with_nothing.config_path_format == self.under_test_data["config_path_format"]

    def test_value_attributes(self, sut: TemplateSetting):
        assert sut.base_file_path == self.under_test_data["base_file_path"]
        assert sut.config_path == self.under_test_data["config_path"]
        assert sut.config_path_format == self.under_test_data["config_path_format"]

    def _expected_serialize_value(self) -> dict:
        return self.under_test_data

    def _expected_deserialize_value(self, obj: TemplateSetting) -> None:
        assert isinstance(obj, self.sut_object)
        assert obj.base_file_path == self.under_test_data["base_file_path"]
        assert obj.config_path == self.under_test_data["config_path"]
        assert obj.config_path_format == self.under_test_data["config_path_format"]


class TestTemplateAPI(TemplateSettingTestSuite):
    @property
    def under_test_data(self) -> dict:
        return _Mock_Template_API_Setting

    @property
    def sut_object(self) -> Type[TemplateSetting]:
        return TemplateAPI


class TestTemplateRequest(TemplateSettingTestSuite):
    @property
    def under_test_data(self) -> dict:
        return _Mock_Template_API_Request_Setting

    @property
    def sut_object(self) -> Type[TemplateSetting]:
        return TemplateRequest


class TestTemplateResponse(TemplateSettingTestSuite):
    @property
    def under_test_data(self) -> dict:
        return _Mock_Template_API_Response_Setting

    @property
    def sut_object(self) -> Type[TemplateSetting]:
        return TemplateResponse


class TestTemplateValues(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> TemplateValues:
        return TemplateValues(
            api=MOCK_MODEL.template_values_api,
            request=MOCK_MODEL.template_values_request,
            response=MOCK_MODEL.template_values_response,
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> TemplateValues:
        return TemplateValues()

    def test_eq_operation_with_valid_object(self, sut: _Config, sut_with_nothing: _Config):
        # NOTE: TemplateConfig has default value
        assert sut == sut_with_nothing

    def test_value_attributes(self, sut: TemplateValues):
        assert sut.api == MOCK_MODEL.template_values_api
        assert sut.request == MOCK_MODEL.template_values_request
        assert sut.response == MOCK_MODEL.template_values_response

    def test_serialize_with_none(self, sut_with_nothing: TemplateValues):
        sut_with_nothing.api = None
        sut_with_nothing.request = None
        sut_with_nothing.response = None
        super().test_serialize_with_none(sut_with_nothing)

    def _expected_serialize_value(self) -> dict:
        return _Mock_Template_Values_Setting

    def _expected_deserialize_value(self, obj: TemplateValues) -> None:
        assert isinstance(obj, TemplateValues)
        assert obj.api.serialize() == _Mock_Template_Values_Setting.get("api")
        assert obj.request.serialize() == _Mock_Template_Values_Setting.get("request")
        assert obj.response.serialize() == _Mock_Template_Values_Setting.get("response")


class TestTemplateApply(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> TemplateApply:
        return TemplateApply(
            scan_strategy=_Mock_Template_Apply_Scan_Strategy,
            api=_Mock_Template_Apply_Has_Tag_Setting.get("api"),
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> TemplateApply:
        return TemplateApply(scan_strategy=_Mock_Template_Apply_Scan_Strategy)

    def test_value_attributes(self, sut: TemplateApply):
        assert sut.scan_strategy == _Mock_Template_Apply_Scan_Strategy
        assert sut.api == _Mock_Template_Apply_Has_Tag_Setting.get("api")

    def test_serialize_with_none(self, sut_with_nothing: TemplateApply):
        serialized_data = sut_with_nothing.serialize()
        assert serialized_data is not None
        assert serialized_data["scan_strategy"] == _Mock_Template_Apply_Has_Tag_Setting.get("scan_strategy")
        assert serialized_data["api"] == []

    def _expected_serialize_value(self) -> dict:
        return _Mock_Template_Apply_Has_Tag_Setting

    def _expected_deserialize_value(self, obj: TemplateApply) -> None:
        assert isinstance(obj, TemplateApply)
        assert obj.scan_strategy == _Mock_Template_Apply_Scan_Strategy
        assert obj.api == _Mock_Template_Apply_Has_Tag_Setting.get("api")

    def test_deserialize_with_missing_strategy(self):
        with pytest.raises(ValueError) as exc_info:
            TemplateApply().deserialize(data={"miss strategy": ""})
        assert re.search(r".{0,32}scan_strategy.{0,32}cannot be empty.{0,32}", str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize(
        ("scan_strategy", "expected_exception", "regular_expression"),
        [
            (None, ValueError, r".{0,64}argument \*scan_strategy\* is missing.{0,64}"),
            ("invalid strategy", TypeError, r".{0,128}data type is invalid.{0,128}"),
        ],
    )
    def test_serialize_with_invalid_scan_strategy(
        self,
        scan_strategy: Any,
        expected_exception: Exception,
        regular_expression: str,
        sut_with_nothing: TemplateApply,
    ):
        with pytest.raises(expected_exception) as exc_info:
            sut_with_nothing.scan_strategy = scan_strategy
            sut_with_nothing.serialize()
        assert re.search(regular_expression, str(exc_info.value), re.IGNORECASE)


class TestTemplateConfig(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> TemplateConfig:
        return TemplateConfig(values=MOCK_MODEL.template_values, apply=MOCK_MODEL.template_apply)

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> TemplateConfig:
        return TemplateConfig()

    def test_value_attributes(self, sut: TemplateConfig):
        # Verify section *values*
        assert sut.values.api == MOCK_MODEL.template_values_api
        assert sut.values.request == MOCK_MODEL.template_values_request
        assert sut.values.response == MOCK_MODEL.template_values_response

        # Verify section *apply*
        assert sut.apply == MOCK_MODEL.template_apply

    def test_serialize_with_none(self, sut_with_nothing: TemplateConfig):
        sut_with_nothing.values = None
        sut_with_nothing.apply = None
        super().test_serialize_with_none(sut_with_nothing)

    def _expected_serialize_value(self) -> dict:
        return _Mock_Template_Setting

    def _expected_deserialize_value(self, obj: TemplateConfig) -> None:
        assert isinstance(obj, TemplateConfig)
        assert obj.values.serialize() == _Mock_Template_Setting.get("values")
        assert obj.apply.serialize() == _Mock_Template_Setting.get("apply")


class TestMockAPI(TemplatableConfigTestSuite):
    @pytest.fixture(scope="function")
    def sut(self) -> MockAPI:
        return MockAPI(url=_Test_URL, http=self._Mock_Model.http, tag=_Test_Tag)

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> MockAPI:
        return MockAPI()

    def test_value_attributes(self, sut: MockAPI):
        assert sut.url == _Test_URL, _assertion_msg
        assert sut.http == self._Mock_Model.http, _assertion_msg

    @pytest.mark.parametrize(
        ("setting_val", "should_call_deserialize"),
        [
            ({"test": "test"}, True),
            (Mock(HTTP()), False),
        ],
    )
    @patch.object(HTTP, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_http_with_valid_obj(
        self,
        mock_deserialize: Mock,
        setting_val: Union[dict, HTTP],
        should_call_deserialize: bool,
        sut_with_nothing: MockAPI,
    ):
        # Run target function
        sut_with_nothing.http = setting_val
        # Verify the running result
        if should_call_deserialize:
            mock_deserialize.assert_called_once_with(data=setting_val)
            assert sut_with_nothing.http == MOCK_RETURN_VALUE
        else:
            mock_deserialize.assert_not_called()
            assert sut_with_nothing.http == setting_val

    @patch.object(HTTP, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_http_with_invalid_obj(self, mock_deserialize: Mock, sut_with_nothing: MockAPI):
        with pytest.raises(TypeError) as exc_info:
            sut_with_nothing.http = "Invalid object"
        mock_deserialize.assert_not_called()
        assert re.search(r"Setter .{1,32} only accepts .{1,32} type object.", str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize("invalid_value", [[], (), 123])
    def test_prop_tag_with_invalid_obj(self, invalid_value: object, sut_with_nothing: MockAPI):
        with pytest.raises(TypeError) as exc_info:
            sut_with_nothing.tag = invalid_value
        assert re.search("only accepts str type value", str(exc_info.value), re.IGNORECASE)

    def _expected_serialize_value(self) -> dict:
        return _TestConfig.Mock_API

    def _expected_deserialize_value(self, obj: MockAPI) -> None:
        assert isinstance(obj, MockAPI)
        assert obj.url == _Test_URL
        assert obj.http.request.method == _TestConfig.Request.get("method", None)
        assert obj.http.request.parameters == [self._Mock_Model.api_parameter]
        assert obj.http.response.value == _TestConfig.Response.get("value", None)
        assert obj.tag == _Test_Tag

    @pytest.mark.parametrize(
        ("formatter", "format_object"),
        [
            (Format.JSON, JSON),
            (Format.YAML, YAML),
        ],
    )
    def test_valid_format(self, formatter: str, format_object, sut: MockAPI):
        with patch.object(format_object, "serialize") as mock_formatter:
            format_str = sut.format(formatter)
            assert format_str
            mock_formatter.assert_called_once_with(sut.serialize())

    def test_invalid_format(self, sut: MockAPI):
        invalid_format = "not support or invalid format type"
        with pytest.raises(ValueError) as exc_info:
            sut.format(invalid_format)
        assert re.search(r".{0,64}not support.{0,64}" + re.escape(invalid_format), str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize("http_req", [None, HTTP(), HTTP(request=HTTPRequest())])
    def test_set_valid_request(self, http_req: Optional[HTTPRequest], sut_with_nothing: MockAPI):
        # Pro-process
        sut_with_nothing.http = http_req

        assert sut_with_nothing.http == http_req
        ut_method = "POST"
        ut_parameters = [{"name": "arg1", "required": False, "default": "val1", "type": "str"}]
        sut_with_nothing.set_request(method=ut_method, parameters=ut_parameters)

        assert sut_with_nothing.http
        assert sut_with_nothing.http.request
        assert sut_with_nothing.http.request.method == ut_method
        assert sut_with_nothing.http.request.parameters == [
            APIParameter(name="arg1", required=False, default="val1", value_type="str")
        ]
        assert sut_with_nothing.tag == ""

    @pytest.mark.parametrize(
        "api_params",
        [
            None,
            [],
            [{"name": "arg1", "required": False, "default": "val1", "type": "str"}],
            [APIParameter(name="arg2", required=False, default=0, value_type="int")],
            [
                {"name": "arg1", "required": False, "default": "val1", "type": "str"},
                APIParameter(name="arg2", required=False, default=0, value_type="int"),
            ],
        ],
    )
    def test_set_valid_request_with_params(
        self, api_params: Optional[List[Union[dict, APIParameter]]], sut_with_nothing: MockAPI
    ):
        ut_method = "POST"
        ut_parameters = api_params
        sut_with_nothing.set_request(method=ut_method, parameters=ut_parameters)

        assert sut_with_nothing.http
        assert sut_with_nothing.http.request
        assert sut_with_nothing.http.request.method == ut_method
        api_params_in_config = sut_with_nothing.http.request.parameters
        assert len(api_params_in_config) == len(api_params or [])
        if api_params:
            for p in api_params_in_config:
                one_params = list(
                    filter(lambda _p: p.name == (_p.name if isinstance(_p, APIParameter) else _p["name"]), api_params)
                )
                assert one_params
                expect_param = one_params[0]
                assert p.name == (expect_param.name if isinstance(expect_param, APIParameter) else expect_param["name"])
                assert p.required is (
                    expect_param.required if isinstance(expect_param, APIParameter) else expect_param["required"]
                )
                assert p.value_type == (
                    expect_param.value_type if isinstance(expect_param, APIParameter) else expect_param["type"]
                )
                assert p.default == (
                    expect_param.default if isinstance(expect_param, APIParameter) else expect_param["default"]
                )
        assert sut_with_nothing.tag == ""

    @pytest.mark.parametrize(
        "params",
        [
            {"name": "arg1", "required": False, "default": "val1", "type": "str", "invalid_key": ""},
            {"name": "arg1", "required": False, "default": "val1", "value_type": "str"},
        ],
    )
    def test_set_invalid_request(self, params: dict, sut_with_nothing: MockAPI):
        ut_method = "POST"
        ut_parameters = [params]
        with pytest.raises(ValueError) as exc_info:
            sut_with_nothing.set_request(method=ut_method, parameters=ut_parameters)
        assert re.search(r".{1,64}format.{1,64}is incorrect.{1,64}", str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize(
        ("http_resp", "response_strategy", "response_value"),
        [
            # string strategy response
            (None, ResponseStrategy.STRING, "PyTest response"),
            (HTTP(), ResponseStrategy.STRING, "PyTest response"),
            (HTTP(response=HTTPResponse(strategy=ResponseStrategy.STRING)), ResponseStrategy.STRING, "PyTest response"),
            # file strategy response
            (None, ResponseStrategy.FILE, "File path"),
            (HTTP(), ResponseStrategy.FILE, "File path"),
            (HTTP(response=HTTPResponse(strategy=ResponseStrategy.STRING)), ResponseStrategy.FILE, "File path"),
            # object strategy response with object value
            (None, ResponseStrategy.OBJECT, MockModel().response_properties),
            (HTTP(), ResponseStrategy.OBJECT, MockModel().response_properties),
            (
                HTTP(response=HTTPResponse(strategy=ResponseStrategy.STRING)),
                ResponseStrategy.OBJECT,
                MockModel().response_properties,
            ),
            # object strategy response with dict value
            (None, ResponseStrategy.OBJECT, _Test_Response_Properties),
            (HTTP(), ResponseStrategy.OBJECT, _Test_Response_Properties),
            (
                HTTP(response=HTTPResponse(strategy=ResponseStrategy.STRING)),
                ResponseStrategy.OBJECT,
                _Test_Response_Properties,
            ),
        ],
    )
    def test_set_valid_response(
        self,
        http_resp: Optional[HTTPResponse],
        response_strategy: ResponseStrategy,
        response_value: Union[str, list],
        sut_with_nothing: MockAPI,
    ):
        # Pro-process
        sut_with_nothing.http = http_resp

        assert sut_with_nothing.http == http_resp
        if response_strategy is ResponseStrategy.OBJECT:
            sut_with_nothing.set_response(strategy=response_strategy, iterable_value=response_value)
        else:
            sut_with_nothing.set_response(strategy=response_strategy, value=response_value)

        assert sut_with_nothing.http
        assert sut_with_nothing.http.response
        if response_strategy is ResponseStrategy.STRING:
            under_test_response_value = sut_with_nothing.http.response.value
        elif response_strategy is ResponseStrategy.FILE:
            under_test_response_value = sut_with_nothing.http.response.path
        elif response_strategy is ResponseStrategy.OBJECT:
            under_test_response_value = sut_with_nothing.http.response.properties
            response_value = [ResponseProperty().deserialize(v) if isinstance(v, dict) else v for v in response_value]
        else:
            assert False, "Invalid response strategy."
        assert under_test_response_value == response_value
        assert sut_with_nothing.tag == ""

    def test_set_invalid_response(self, sut_with_nothing: MockAPI):
        with pytest.raises(TypeError) as exc_info:
            sut_with_nothing.set_response(strategy="Invalid response strategy")
        assert re.search(r".{0,32}invalid response strategy.{0,32}", str(exc_info.value), re.IGNORECASE)


class TestHTTP(TemplatableConfigTestSuite):
    @pytest.fixture(scope="function")
    def sut(self) -> HTTP:
        return HTTP(request=self._Mock_Model.http_request, response=self._Mock_Model.http_response)

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> HTTP:
        return HTTP()

    def test_value_attributes(self, sut: HTTP):
        assert sut.request == self._Mock_Model.http_request, _assertion_msg
        assert sut.response == self._Mock_Model.http_response, _assertion_msg

    @pytest.mark.parametrize(
        ("setting_val", "should_call_deserialize"),
        [
            ({"test": "test"}, True),
            (Mock(HTTPRequest()), False),
        ],
    )
    @patch.object(HTTPRequest, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_request_with_valid_obj(
        self,
        mock_deserialize: Mock,
        setting_val: Union[dict, HTTPRequest],
        should_call_deserialize: bool,
        sut_with_nothing: HTTP,
    ):
        # Run target function
        sut_with_nothing.request = setting_val
        # Verify the running result
        if should_call_deserialize:
            mock_deserialize.assert_called_once_with(data=setting_val)
            assert sut_with_nothing.request == MOCK_RETURN_VALUE
        else:
            mock_deserialize.assert_not_called()
            assert sut_with_nothing.request == setting_val

    @patch.object(HTTPRequest, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_request_with_invalid_obj(self, mock_deserialize: Mock, sut_with_nothing: HTTP):
        with pytest.raises(TypeError) as exc_info:
            sut_with_nothing.request = "Invalid object"
        mock_deserialize.assert_not_called()
        assert re.search(r"Setter .{1,32} only accepts .{1,32} type object.", str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize(
        ("setting_val", "should_call_deserialize"),
        [
            ({"test": "test"}, True),
            (MOCK_MODEL.http_response, False),
        ],
    )
    @patch.object(HTTPResponse, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_response_with_valid_obj(
        self,
        mock_deserialize: Mock,
        setting_val: Union[dict, HTTPResponse],
        should_call_deserialize: bool,
        sut_with_nothing: HTTP,
    ):
        # Run target function
        sut_with_nothing.response = setting_val
        # Verify the running result
        if should_call_deserialize:
            mock_deserialize.assert_called_once_with(data=setting_val)
            assert sut_with_nothing.response == MOCK_RETURN_VALUE
        else:
            mock_deserialize.assert_not_called()
            assert sut_with_nothing.response == setting_val

    @patch.object(HTTPResponse, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_response_with_invalid_obj(self, mock_deserialize: Mock, sut_with_nothing: HTTP):
        with pytest.raises(TypeError) as exc_info:
            sut_with_nothing.response = "Invalid object"
        mock_deserialize.assert_not_called()
        assert re.search(r"Setter .{1,32} only accepts .{1,32} type object.", str(exc_info.value), re.IGNORECASE)

    def _expected_serialize_value(self) -> dict:
        return _TestConfig.Http

    def _expected_deserialize_value(self, obj: HTTP) -> None:
        assert isinstance(obj, HTTP)
        assert obj.request.method == _TestConfig.Request.get("method", None)
        assert obj.request.parameters == [self._Mock_Model.api_parameter]
        assert obj.response.value == _TestConfig.Response.get("value", None)


class TestHTTPReqeust(TemplatableConfigTestSuite):
    @pytest.fixture(scope="function")
    def sut(self) -> HTTPRequest:
        return HTTPRequest(method=_TestConfig.Request.get("method", None), parameters=[self._Mock_Model.api_parameter])

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> HTTPRequest:
        return HTTPRequest()

    def test_value_attributes(self, sut: HTTPRequest):
        assert sut.method == _TestConfig.Request.get("method", None), _assertion_msg
        assert sut.parameters == [self._Mock_Model.api_parameter], _assertion_msg

    def _expected_serialize_value(self) -> dict:
        return _TestConfig.Request

    def _expected_deserialize_value(self, obj: HTTPRequest) -> None:
        assert isinstance(obj, HTTPRequest)
        assert obj.method == _TestConfig.Request.get("method", None)
        assert obj.parameters == [self._Mock_Model.api_parameter]

    def test_deserialize_fail(self, sut_with_nothing: HTTPRequest):
        utd = {
            "method": "HTTP method",
            "parameters": "a value which data type is not list",
        }
        with pytest.raises(TypeError) as exc_info:
            sut_with_nothing.deserialize(data=utd)
        assert str(exc_info.value) == "Argument *parameters* should be a list type value."

    def test_get_one_param_by_name(self, sut: HTTPRequest):
        param = sut.get_one_param_by_name(_Test_API_Parameter["name"])
        assert param == self._Mock_Model.api_parameter

    def test_fail_get_one_param_by_name(self, sut: HTTPRequest):
        param = sut.get_one_param_by_name("Not exist argument")
        assert param is None


class TestAPIParameter(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> APIParameter:
        return APIParameter(
            name=_Test_API_Parameter["name"],
            required=_Test_API_Parameter["required"],
            default=_Test_API_Parameter["default"],
            value_type=_Test_API_Parameter["type"],
            value_format=_Test_API_Parameter["format"],
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> APIParameter:
        return APIParameter()

    def test_value_attributes(self, sut: APIParameter):
        assert sut.name == _Test_API_Parameter["name"], _assertion_msg
        assert sut.required is _Test_API_Parameter["required"], _assertion_msg
        assert sut.default == _Test_API_Parameter["default"], _assertion_msg
        assert sut.value_type == _Test_API_Parameter["type"], _assertion_msg
        assert sut.value_format == _Test_API_Parameter["format"], _assertion_msg
        assert sut.items is None, _assertion_msg

    def _expected_serialize_value(self) -> dict:
        return _Test_API_Parameter

    def _expected_deserialize_value(self, obj: APIParameter) -> None:
        assert isinstance(obj, APIParameter)
        assert obj.name == _Test_API_Parameter["name"]
        assert obj.required is _Test_API_Parameter["required"]
        assert obj.default == _Test_API_Parameter["default"]
        assert obj.value_type == _Test_API_Parameter["type"]
        assert obj.value_format == _Test_API_Parameter["format"]
        assert obj.items is None

    def test_serialize_api_parameter_with_iterable_items(self, sut_with_nothing: APIParameter):
        sut_with_nothing.deserialize(_Test_Iterable_Parameter_With_MultiValue)
        serialized_data = sut_with_nothing.serialize()
        assert serialized_data == _Test_Iterable_Parameter_With_MultiValue

    def test_deserialize_api_parameter_with_iterable_items(self, sut_with_nothing: APIParameter):
        sut_with_nothing.deserialize(_Test_Iterable_Parameter_With_MultiValue)
        assert sut_with_nothing.name == _Test_Iterable_Parameter_With_MultiValue["name"]
        assert sut_with_nothing.required == _Test_Iterable_Parameter_With_MultiValue["required"]
        assert sut_with_nothing.default == _Test_Iterable_Parameter_With_MultiValue["default"]
        assert sut_with_nothing.value_type == _Test_Iterable_Parameter_With_MultiValue["type"]
        assert sut_with_nothing.value_format == _Test_Iterable_Parameter_With_MultiValue["format"]
        assert len(sut_with_nothing.items) == len(_Test_Iterable_Parameter_Items)
        assert [item.serialize() for item in sut_with_nothing.items] == _Test_Iterable_Parameter_With_MultiValue[
            "items"
        ]

    @pytest.mark.parametrize("items_value", [_Test_Iterable_Parameter_With_MultiValue])
    def test_converting_at_prop_items_with_valid_value(self, items_value: dict):
        under_test = APIParameter(
            name=items_value["name"],
            required=items_value["required"],
            default=items_value["default"],
            value_type=items_value["type"],
            value_format=items_value["format"],
            items=items_value["items"],
        )
        assert isinstance(under_test.items, list)
        assert False not in list(map(lambda i: isinstance(i, IteratorItem), under_test.items))
        for i in under_test.items:
            assert i.name in [
                _Test_Iterable_Parameter_Item_Name["name"],
                _Test_Iterable_Parameter_Item_Value["name"],
            ], _assertion_msg
            if i.name == _Test_Iterable_Parameter_Item_Name["name"]:
                criteria = _Test_Iterable_Parameter_Item_Name
            elif i.name == _Test_Iterable_Parameter_Item_Value["name"]:
                criteria = _Test_Iterable_Parameter_Item_Value
            else:
                raise ValueError("")
            assert i.required == criteria["required"]
            assert i.value_type == criteria["type"]

    def test_converting_at_prop_items_with_invalid_value(self):
        with pytest.raises(TypeError) as exc_info:
            APIParameter(
                name="name",
                required=False,
                value_type="str",
                items=[1, [], ()],
            )
        assert re.search(
            r".{0,64}data type.{0,64}key \*items\*.{0,64}be dict or IteratorItem.{0,64}",
            str(exc_info.value),
            re.IGNORECASE,
        )


class TestIteratorItem(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> IteratorItem:
        return IteratorItem(
            name=_Test_Iterable_Parameter_Item_Name["name"],
            required=_Test_Iterable_Parameter_Item_Name["required"],
            value_type=_Test_Iterable_Parameter_Item_Name["type"],
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> IteratorItem:
        return IteratorItem()

    def test_value_attributes(self, sut: IteratorItem):
        assert sut.name == _Test_Iterable_Parameter_Item_Name["name"], _assertion_msg
        assert sut.required is _Test_Iterable_Parameter_Item_Name["required"], _assertion_msg
        assert sut.value_type == _Test_Iterable_Parameter_Item_Name["type"], _assertion_msg

    def _expected_serialize_value(self) -> Any:
        return _Test_Iterable_Parameter_Item_Name

    def _expected_deserialize_value(self, obj: IteratorItem) -> None:
        assert isinstance(obj, IteratorItem)
        assert obj.name == _Test_Iterable_Parameter_Item_Name["name"]
        assert obj.required is _Test_Iterable_Parameter_Item_Name["required"]
        assert obj.value_type == _Test_Iterable_Parameter_Item_Name["type"]


class TestResponseProperty(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> ResponseProperty:
        return ResponseProperty(
            name=_Test_Response_Property_List["name"],
            required=_Test_Response_Property_List["required"],
            value_type=_Test_Response_Property_List["type"],
            value_format=_Test_Response_Property_List["format"],
            items=_Test_Response_Property_List["items"],
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> ResponseProperty:
        return ResponseProperty()

    def test_value_attributes(self, sut: ResponseProperty):
        assert sut.name == _Test_Response_Property_List["name"], _assertion_msg
        assert sut.required is _Test_Response_Property_List["required"], _assertion_msg
        assert sut.value_type == _Test_Response_Property_List["type"], _assertion_msg
        assert sut.value_format == _Test_Response_Property_List["format"], _assertion_msg
        assert isinstance(sut.items, list)
        for item in sut.items:
            assert list(filter(lambda i: i["name"] == item.name, _Test_Response_Property_List["items"]))
            assert list(filter(lambda i: i["required"] == item.required, _Test_Response_Property_List["items"]))
            assert list(filter(lambda i: i["type"] == item.value_type, _Test_Response_Property_List["items"]))

    def _expected_serialize_value(self) -> Any:
        return _Test_Response_Property_List

    def _expected_deserialize_value(self, obj: ResponseProperty) -> None:
        assert isinstance(obj, ResponseProperty)
        assert obj.name == _Test_Response_Property_List["name"]
        assert obj.required is _Test_Response_Property_List["required"]
        assert obj.value_type == _Test_Response_Property_List["type"]
        assert obj.value_format == _Test_Response_Property_List["format"]
        assert isinstance(obj.items, list)
        for item in obj.items:
            assert list(filter(lambda i: i["name"] == item.name, _Test_Response_Property_List["items"]))
            assert list(filter(lambda i: i["required"] == item.required, _Test_Response_Property_List["items"]))
            assert list(filter(lambda i: i["type"] == item.value_type, _Test_Response_Property_List["items"]))

    def test_convert_invalid_items(self, sut_with_nothing: ResponseProperty):
        with pytest.raises(TypeError) as exc_info:
            ResponseProperty(items=["invalid element"])
        assert re.search(
            r".{0,32}key \*items\*.{0,32}be dict or IteratorItem.{0,32}", str(exc_info.value), re.IGNORECASE
        )


class TestHTTPResponse(TemplatableConfigTestSuite):
    @pytest.fixture(scope="function")
    def sut(self) -> HTTPResponse:
        return HTTPResponse(strategy=ResponseStrategy.STRING, value=_Test_HTTP_Resp)

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> HTTPResponse:
        return HTTPResponse(strategy=ResponseStrategy.STRING)

    def test_value_attributes(self, sut: HTTPResponse):
        assert sut.value == _Test_HTTP_Resp, _assertion_msg

    def test_serialize_with_none(self, sut_with_nothing: _Config):
        serialized_data = sut_with_nothing.serialize()
        assert serialized_data is not None
        assert serialized_data["strategy"] == ResponseStrategy.STRING.value
        assert serialized_data["value"] == ""

    def _expected_serialize_value(self) -> dict:
        return _TestConfig.Response

    def _expected_deserialize_value(self, obj: HTTPResponse) -> None:
        assert isinstance(obj, HTTPResponse)
        assert obj.value == _TestConfig.Response.get("value", None)

    @pytest.mark.parametrize(
        ("compare", "be_compared"),
        [
            (None, random.choice([s for s in ResponseStrategy])),
            (None, None),
        ],
    )
    def test_invalid_compare_with_missing_strategy(self, compare: ResponseStrategy, be_compared: ResponseStrategy):
        with pytest.raises(ValueError) as exc_info:
            HTTPResponse(strategy=compare) == HTTPResponse(strategy=be_compared)
        assert re.search(r".{0,32}Miss.{0,32}strategy.{0,32}", str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize(
        ("compare", "be_compared"),
        [
            (ResponseStrategy.STRING, None),
            (ResponseStrategy.FILE, None),
            (ResponseStrategy.OBJECT, None),
            (ResponseStrategy.STRING, ResponseStrategy.FILE),
            (ResponseStrategy.FILE, ResponseStrategy.OBJECT),
            (ResponseStrategy.OBJECT, ResponseStrategy.STRING),
        ],
    )
    def test_invalid_compare(self, compare: ResponseStrategy, be_compared: ResponseStrategy):
        with pytest.raises(TypeError) as exc_info:
            HTTPResponse(strategy=compare) == HTTPResponse(strategy=be_compared)
        assert re.search(
            r".{0,32}different HTTP response strategy.{0,32}cannot compare.{0,32}", str(exc_info.value), re.IGNORECASE
        )

    @pytest.mark.parametrize(
        ("strategy", "expected_strategy"),
        [
            ("string", ResponseStrategy.STRING),
            ("file", ResponseStrategy.FILE),
            ("object", ResponseStrategy.OBJECT),
        ],
    )
    def test_set_str_type_strategy(self, strategy: str, expected_strategy: ResponseStrategy):
        resp = HTTPResponse(strategy=strategy)
        assert resp.strategy is expected_strategy

    def test_invalid_set_properties(self):
        with pytest.raises(TypeError) as exc_info:
            HTTPResponse(strategy=ResponseStrategy.OBJECT, properties=["invalid property value"])
        assert re.search(
            r".{0,32}data type.{0,32}\*properties\*.{0,32}be dict or ResponseProperty.{0,32}",
            str(exc_info.value),
            re.IGNORECASE,
        )

    @pytest.mark.parametrize(
        "response",
        [
            HTTPResponse(strategy=None, value="some string value"),
            HTTPResponse(strategy=None, path="file path"),
            HTTPResponse(strategy=None, properties=MockModel().response_properties),
        ],
    )
    def test_serialize_as_none_with_strategy(self, response: HTTPResponse):
        with pytest.raises(ValueError) as exc_info:
            response.serialize()
        assert re.search(r".{0,32}strategy.{0,32}missing.{0,32}", str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize(
        ("response", "verify_key"),
        [
            (HTTPResponse(strategy=ResponseStrategy.STRING, value=None), "value"),
            (HTTPResponse(strategy=ResponseStrategy.FILE, path=None), "path"),
            (HTTPResponse(strategy=ResponseStrategy.OBJECT, properties=None), "properties"),
            (HTTPResponse(strategy=ResponseStrategy.STRING, value=""), "value"),
            (HTTPResponse(strategy=ResponseStrategy.FILE, path=""), "path"),
            (HTTPResponse(strategy=ResponseStrategy.OBJECT, properties=[]), "properties"),
        ],
    )
    def test_serialize_with_strategy_and_empty_value(self, response: HTTPResponse, verify_key: str):
        serialized_data = response.serialize()
        assert serialized_data is not None
        assert serialized_data["strategy"] == response.strategy.value
        verify_value = [] if response.strategy is ResponseStrategy.OBJECT else getattr(response, verify_key)
        assert serialized_data[verify_key] == verify_value

    @pytest.mark.parametrize(
        ("response", "expected_data"),
        [
            (
                HTTPResponse(strategy=ResponseStrategy.STRING, value="OK"),
                {"strategy": ResponseStrategy.STRING.value, "value": "OK"},
            ),
            (
                HTTPResponse(strategy=ResponseStrategy.FILE, path="file path"),
                {"strategy": ResponseStrategy.FILE.value, "path": "file path"},
            ),
            (
                HTTPResponse(strategy=ResponseStrategy.OBJECT, properties=MockModel().response_properties),
                {
                    "strategy": ResponseStrategy.OBJECT.value,
                    "properties": [p.serialize() for p in MockModel().response_properties],
                },
            ),
        ],
    )
    def test_serialize_with_strategy(self, response: HTTPResponse, expected_data: dict):
        assert response.serialize() == expected_data

    @pytest.mark.parametrize(
        ("data", "expected_response"),
        [
            (
                {"strategy": ResponseStrategy.STRING.value, "value": "OK"},
                HTTPResponse(strategy=ResponseStrategy.STRING, value="OK"),
            ),
            (
                {"strategy": ResponseStrategy.FILE.value, "path": "file path"},
                HTTPResponse(strategy=ResponseStrategy.FILE, path="file path"),
            ),
            (
                {
                    "strategy": ResponseStrategy.OBJECT.value,
                    "properties": [p.serialize() for p in MockModel().response_properties],
                },
                HTTPResponse(strategy=ResponseStrategy.OBJECT, properties=MockModel().response_properties),
            ),
        ],
    )
    def test_valid_deserialize_with_strategy(self, data: dict, expected_response: HTTPResponse):
        assert HTTPResponse().deserialize(data=data) == expected_response

    def test_deserialize_with_missing_strategy(self):
        with pytest.raises(ValueError) as exc_info:
            HTTPResponse().deserialize(data={"miss strategy": ""})
        assert re.search(r".{0,32}strategy.{0,32}cannot be empty.{0,32}", str(exc_info.value), re.IGNORECASE)

    def test_serialize_with_invalid_strategy(self, sut_with_nothing: HTTPResponse):
        with pytest.raises(TypeError) as exc_info:
            sut_with_nothing.strategy = "invalid strategy"
            sut_with_nothing.serialize()
        assert re.search(r".{0,128}data type is invalid.{0,128}", str(exc_info.value), re.IGNORECASE)
