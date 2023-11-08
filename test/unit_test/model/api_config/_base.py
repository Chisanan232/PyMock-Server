import glob
import os
import pathlib
import re
from abc import ABC, ABCMeta, abstractmethod
from enum import Enum
from test._values import (
    _Base_URL,
    _Mock_Load_Config,
    _Mock_Template_Apply_Has_Tag_Setting,
    _Mock_Template_Config_Activate,
    _Test_API_Parameter,
    _Test_HTTP_Resp,
    _Test_Tag,
    _Test_URL,
    _TestConfig,
)
from typing import Any, Callable, Dict, List, Optional
from unittest.mock import MagicMock, Mock, PropertyMock, call, patch

import pytest

from pymock_api._utils import YAML
from pymock_api.model import HTTP, MockAPI, MockAPIs
from pymock_api.model.api_config import (
    BaseConfig,
    ResponseProperty,
    TemplateConfig,
    _Checkable,
    _Config,
)
from pymock_api.model.api_config.apis import APIParameter, HTTPRequest, HTTPResponse
from pymock_api.model.api_config.template import (
    LoadConfig,
    TemplateAPI,
    TemplateApply,
    TemplateConfigLoadable,
    TemplateRequest,
    TemplateResponse,
    TemplateValues,
)
from pymock_api.model.enums import (
    ConfigLoadingOrder,
    ResponseStrategy,
    set_loading_function,
)

_assertion_msg = "Its property's value should be same as we set."
MOCK_RETURN_VALUE: Mock = Mock()


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
            api=_Mock_Template_Apply_Has_Tag_Setting["api"],
        )

    @property
    def template_load_config(self) -> LoadConfig:
        return LoadConfig(
            includes_apis=_Mock_Load_Config["includes_apis"],
            order=_Mock_Load_Config["order"],
        )

    @property
    def template_config(self) -> TemplateConfig:
        return TemplateConfig(
            activate=_Mock_Template_Config_Activate,
            load_config=self.template_load_config,
            values=self.template_values,
            apply=self.template_apply,
        )

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


class LoadConfigFunction(Enum):
    """
    Here values are the function naming of object *TemplateConfigLoadable* which loads configuration
    """

    FROM_DATA: str = "apis:_load_mocked_apis_from_data"
    BY_FILE: str = "file:_load_templatable_config"
    BY_APPLY: str = "apply:_load_templatable_config_by_apply"


class TemplateConfigLoadableTestSuite(ConfigTestSpec, ABC):
    @pytest.mark.parametrize(
        ("load_order", "expected_func_run_order"),
        [
            (
                [ConfigLoadingOrder.APIs, ConfigLoadingOrder.FILE, ConfigLoadingOrder.APPLY],
                [LoadConfigFunction.FROM_DATA, LoadConfigFunction.BY_FILE, LoadConfigFunction.BY_APPLY],
            ),
            (
                [ConfigLoadingOrder.APIs, ConfigLoadingOrder.APPLY, ConfigLoadingOrder.FILE],
                [LoadConfigFunction.FROM_DATA, LoadConfigFunction.BY_APPLY, LoadConfigFunction.BY_FILE],
            ),
            (
                [ConfigLoadingOrder.APIs, ConfigLoadingOrder.FILE],
                [LoadConfigFunction.FROM_DATA, LoadConfigFunction.BY_FILE],
            ),
            (
                [ConfigLoadingOrder.APIs, ConfigLoadingOrder.APPLY],
                [LoadConfigFunction.FROM_DATA, LoadConfigFunction.BY_APPLY],
            ),
        ],
    )
    def test_loading_configuration_workflow(
        self, load_order: List[ConfigLoadingOrder], expected_func_run_order: List[LoadConfigFunction], sut: _Config
    ):
        assert isinstance(sut, TemplateConfigLoadable)
        expected_func_run_order = [func.value.split(":") for func in expected_func_run_order]

        # Parent mock object for mocking target functions
        mock_parent = Mock()
        mock_load_config_data = {}
        # Magic mock the target function
        for func in expected_func_run_order:
            setattr(sut, func[1], MagicMock())
            mock_load_config_data[func[0]] = getattr(sut, func[1])
        # Annotate some functions as magic functions
        for func in expected_func_run_order:
            setattr(mock_parent, func[1], getattr(sut, func[1]))

        # Generate criteria of the function running order
        criteria_order = []
        for func in expected_func_run_order:
            if func[1] == "_load_mocked_apis_from_data":
                criteria = getattr(call, func[1])({})
            else:
                criteria = getattr(call, func[1])()
            criteria_order.append(criteria)

        # Pre-process of setting loading function
        set_loading_function(**mock_load_config_data)
        template_config = TemplateConfig(
            activate=True,
            load_config=LoadConfig(includes_apis=True, order=load_order),
        )
        with patch(
            "pymock_api.model.api_config.MockAPIs._template_config",
            new_callable=PropertyMock,
            return_value=template_config,
        ):
            # Run the target function
            sut._load_mocked_apis_config({})
            # Verify the running result
            mock_parent.assert_has_calls(criteria_order)


_TEST_DATA: List[tuple] = []


def _set_test_data(is_valid: bool, data_model: str, opt_globals_callback: Optional[Callable] = None) -> None:
    def _operate_default_global_var(test_scenario: tuple) -> None:
        global _TEST_DATA
        _TEST_DATA.append(test_scenario)

    global_var_operation = opt_globals_callback if opt_globals_callback else _operate_default_global_var

    if is_valid:
        config_type = "valid"
        expected_is_work = True
    else:
        config_type = "invalid"
        expected_is_work = False
    yaml_dir = os.path.join(
        str(pathlib.Path(__file__).parent.parent.parent.parent),
        "data",
        "check_test",
        "data_model",
        f"{data_model}",
        f"{config_type}",
        "*.yaml",
    )
    for yaml_config_path in glob.glob(yaml_dir):
        global_var_operation((yaml_config_path, expected_is_work))


def set_checking_test_data(data_modal_dir: str, reset: bool = True) -> None:
    if reset:
        reset_test_data()
    init_checking_test_data(data_modal_dir)


def init_checking_test_data(data_modal_dir: str, opt_globals_callback: Optional[Callable] = None) -> None:
    _set_test_data(is_valid=True, data_model=data_modal_dir, opt_globals_callback=opt_globals_callback)
    _set_test_data(is_valid=False, data_model=data_modal_dir, opt_globals_callback=opt_globals_callback)


def reset_test_data() -> None:
    global _TEST_DATA
    _TEST_DATA.clear()


class CheckableTestSuite(ConfigTestSpec, ABC):
    test_data_dir = NotImplementedError("Please override attribute *test_data_dir* about the test data directory.")

    @pytest.mark.parametrize(
        ("test_data_path", "criteria"),
        _TEST_DATA,
    )
    def test_is_work(self, sut_with_nothing: _Config, test_data_path: str, criteria: bool):
        data_model = sut_with_nothing.deserialize(data=YAML().read(path=test_data_path))
        if data_model:  # For data modal *BaseConfig*
            assert isinstance(data_model, _Checkable)
            data_model.stop_if_fail = False
            is_valid_to_work = data_model.is_work()
            assert is_valid_to_work is criteria
