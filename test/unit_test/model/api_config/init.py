import re
from typing import Any, List, Union
from unittest.mock import Mock, patch

import pytest

from pymock_api import APIConfig
from pymock_api.model import BaseConfig, MockAPI, MockAPIs
from pymock_api.model.api_config import TemplateConfig

from ...._values import (
    _Base_URL,
    _Config_Description,
    _Config_Name,
    _Test_Config,
    _Test_HTTP_Resp,
    _Test_URL,
    _TestConfig,
)
from ._base import (
    MOCK_MODEL,
    MOCK_RETURN_VALUE,
    CheckableTestSuite,
    TemplateConfigLoadableTestSuite,
    _assertion_msg,
    set_checking_test_data,
)

_APIConfig_Test_Data: List[tuple] = []
_MockAPIs_Test_Data: List[tuple] = []


def reset_api_config_test_data() -> None:
    global _APIConfig_Test_Data
    _APIConfig_Test_Data.clear()


def add_api_config_test_data(test_scenario: tuple) -> None:
    global _APIConfig_Test_Data
    _APIConfig_Test_Data.append(test_scenario)


def reset_mock_apis_test_data() -> None:
    global _MockAPIs_Test_Data
    _MockAPIs_Test_Data.clear()


def add_mock_apis_test_data(test_scenario: tuple) -> None:
    global _MockAPIs_Test_Data
    _MockAPIs_Test_Data.append(test_scenario)


class TestAPIConfig(CheckableTestSuite):
    test_data_dir = "entire_api"
    set_checking_test_data(
        test_data_dir, reset_callback=reset_api_config_test_data, opt_globals_callback=add_api_config_test_data
    )

    @pytest.fixture(scope="function")
    def sut(self) -> APIConfig:
        return APIConfig(name=_Config_Name, description=_Config_Description, apis=self._Mock_Model.mock_apis)

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> APIConfig:
        return APIConfig()

    def test___len___with_value(self, sut: APIConfig):
        sut.apis = _TestConfig.Mock_APIs
        assert len(sut) == len(
            list(filter(lambda k: k not in ["base", "template"], _TestConfig.Mock_APIs.keys()))
        ), "The size of *APIConfig* data object should be same as *MockAPIs* data object."

    def test___len___with_non_value(self):
        assert len(APIConfig()) == 0, "The size of *APIConfig* data object should be '0' if property *apis* is None."

    def test_has_apis_with_value(self, sut: APIConfig):
        sut.apis = _TestConfig.Mock_APIs
        assert sut.has_apis() is True, "It should be 'True' if its property *apis* has value."

    def test_has_apis_with_no_value(self):
        assert APIConfig().has_apis() is False, "It should be 'False' if its property *apis* is None."

    def test_value_attributes(self, sut: APIConfig):
        assert sut.name == _Config_Name, _assertion_msg
        assert sut.description == _Config_Description, _assertion_msg
        assert sut.apis.base.url == _TestConfig.API_Config.get("mocked_apis").get("base").get("url"), _assertion_msg
        assert (
            list(sut.apis.apis.keys())[0] in _TestConfig.API_Config.get("mocked_apis").get("apis").keys()
        ), _assertion_msg

    @pytest.mark.parametrize(
        ("setting_val", "should_call_deserialize"),
        [
            ({}, False),
            ({"test": "test"}, True),
            (Mock(MockAPIs()), False),
        ],
    )
    @patch.object(MockAPIs, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_apis_with_valid_obj(
        self,
        mock_deserialize: Mock,
        setting_val: Union[dict, BaseConfig],
        should_call_deserialize: bool,
        sut_with_nothing: APIConfig,
    ):
        # Run target function
        sut_with_nothing.apis = setting_val
        # Verify the running result
        if should_call_deserialize:
            mock_deserialize.assert_called_once_with(data=setting_val)
            assert sut_with_nothing.apis == MOCK_RETURN_VALUE
        else:
            mock_deserialize.assert_not_called()
            assert sut_with_nothing.apis == (setting_val if setting_val else None)

    @patch.object(MockAPIs, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_apis_with_invalid_obj(self, mock_deserialize: Mock, sut_with_nothing: APIConfig):
        with pytest.raises(TypeError) as exc_info:
            sut_with_nothing.apis = "Invalid object"
        mock_deserialize.assert_not_called()
        assert re.search(r"Setter .{1,32} only accepts .{1,32} type object.", str(exc_info.value), re.IGNORECASE)

    def _expected_serialize_value(self) -> dict:
        return _TestConfig.API_Config

    def _expected_deserialize_value(self, obj: APIConfig) -> None:
        assert isinstance(obj, APIConfig)
        assert obj.name == _Config_Name
        assert obj.description == _Config_Description
        assert obj.apis.base.url == _TestConfig.API_Config.get("mocked_apis").get("base").get("url")
        assert (
            list(obj.apis.apis.keys())[0] in _TestConfig.API_Config.get("mocked_apis").get("apis").keys()
        ), _assertion_msg

    @pytest.mark.parametrize(
        ("test_data_path", "criteria"),
        _APIConfig_Test_Data,
    )
    def test_is_work(self, sut_with_nothing: APIConfig, test_data_path: str, criteria: bool):
        super().test_is_work(sut_with_nothing, test_data_path, criteria)

    @patch("pymock_api._utils.file_opt.YAML.read", return_value=_TestConfig.API_Config)
    def test_from_yaml_file(self, mock_read_yaml: Mock, sut: APIConfig):
        config = sut.from_yaml(path="test-api.yaml")
        mock_read_yaml.assert_called_once_with("test-api.yaml")
        assert isinstance(config, APIConfig)
        assert config.name == _Config_Name
        assert config.description == _Config_Description
        assert config.apis.serialize() == _TestConfig.Mock_APIs

    @patch("pymock_api._utils.file_opt.YAML.write", return_value=None)
    def test_to_yaml_file(self, mock_write_yaml: Mock, sut: APIConfig):
        sut.to_yaml(path=_Test_Config)
        mock_write_yaml.assert_called_once_with(path=_Test_Config, config=sut.serialize())


class TestMockAPIs(TemplateConfigLoadableTestSuite, CheckableTestSuite):
    test_data_dir = "mocked_apis"
    set_checking_test_data(
        test_data_dir, reset_callback=reset_mock_apis_test_data, opt_globals_callback=add_mock_apis_test_data
    )

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

    def _test_is_work_process(self, sut_with_nothing: MockAPIs, test_data_path: str, criteria: bool):
        sut_with_nothing.config_file_name = "api.yaml"
        super()._test_is_work_process(sut_with_nothing, test_data_path, criteria)

    @pytest.mark.parametrize(
        ("test_data_path", "criteria"),
        _MockAPIs_Test_Data,
    )
    def test_is_work(self, sut_with_nothing: MockAPIs, test_data_path: str, criteria: bool):
        super().test_is_work(sut_with_nothing, test_data_path, criteria)

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
