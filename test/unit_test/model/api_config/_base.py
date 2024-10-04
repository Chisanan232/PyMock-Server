import glob
import logging
import os
import pathlib
import re
from abc import ABC, ABCMeta, abstractmethod
from collections import namedtuple
from copy import copy
from decimal import Decimal
from typing import Callable, Dict, List, Optional, Type, Union
from unittest.mock import Mock, PropertyMock, patch

import pytest

from pymock_api._utils import YAML
from pymock_api.model import HTTP, MockAPI, MockAPIs
from pymock_api.model.api_config import (
    BaseConfig,
    BeDividedableAsTemplatableConfig,
    ResponseProperty,
    TemplatableConfigDividable,
    _Checkable,
    _Config,
)
from pymock_api.model.api_config._base import _HasItemsPropConfig
from pymock_api.model.api_config.apis import (
    APIParameter,
    HTTPRequest,
    HTTPResponse,
    ResponseStrategy,
)
from pymock_api.model.api_config.format import Format, _HasFormatPropConfig
from pymock_api.model.api_config.template import TemplateConfig
from pymock_api.model.api_config.template.common import (
    TemplateCommonConfig,
    TemplateFormatConfig,
)
from pymock_api.model.api_config.template.file import (
    LoadConfig,
    TemplateApply,
    TemplateConfigPathAPI,
    TemplateConfigPathRequest,
    TemplateConfigPathResponse,
    TemplateConfigPathValues,
    TemplateFileConfig,
)
from pymock_api.model.api_config.value import FormatStrategy, ValueFormat
from pymock_api.model.api_config.variable import Variable

from ...._values import (
    _Base_URL,
    _Mock_Load_Config,
    _Mock_Template_Apply_Has_Tag_Setting,
    _Mock_Template_Common_Config_Format_Config,
    _Mock_Template_Config_Activate,
    _Test_API_Parameter,
    _Test_HTTP_Resp,
    _Test_Tag,
    _Test_URL,
    _TestConfig,
)

logger = logging.getLogger(__name__)

_assertion_msg = "Its property's value should be same as we set."
MOCK_RETURN_VALUE: Mock = Mock()


class MockModel:
    @property
    def mock_apis(self) -> MockAPIs:
        return MockAPIs(template=self.template_config, base=self.base_config, apis=self.mock_api)

    @property
    def template_values_api(self) -> TemplateConfigPathAPI:
        return TemplateConfigPathAPI()

    @property
    def template_values_request(self) -> TemplateConfigPathRequest:
        return TemplateConfigPathRequest()

    @property
    def template_values_response(self) -> TemplateConfigPathResponse:
        return TemplateConfigPathResponse()

    @property
    def template_values(self) -> TemplateConfigPathValues:
        return TemplateConfigPathValues(
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
    def template_file_config(self) -> TemplateFileConfig:
        return TemplateFileConfig(
            activate=_Mock_Template_Config_Activate,
            load_config=self.template_load_config,
            config_path_values=self.template_values,
            apply=self.template_apply,
        )

    @property
    def template_format_config(self) -> TemplateFormatConfig:
        return TemplateFormatConfig(
            entities=_Mock_Template_Common_Config_Format_Config["entities"],
            variables=_Mock_Template_Common_Config_Format_Config["variables"],
        )

    @property
    def template_common_config(self) -> TemplateCommonConfig:
        return TemplateCommonConfig(
            activate=_Mock_Template_Config_Activate,
            format=self.template_format_config,
        )

    @property
    def template_config(self) -> TemplateConfig:
        return TemplateConfig(
            activate=_Mock_Template_Config_Activate,
            file=self.template_file_config,
            common_config=self.template_common_config,
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
        assert sut.serialize() == self._clean_prop_with_empty_value(self._expected_serialize_value())

    def _clean_prop_with_empty_value(self, data: dict) -> dict:
        final_expect_value = copy(data)
        for k, v in data.items():
            if v in (None, "", [], (), {}):
                final_expect_value.pop(k)
            else:
                if isinstance(v, dict):
                    v = self._clean_prop_with_empty_value(v)
                    final_expect_value[k] = v
                elif isinstance(v, list):
                    dict_type_es = list(filter(lambda e: isinstance(e, dict), v))
                    if dict_type_es:
                        clean_list = []
                        for e in dict_type_es:
                            clean_e = self._clean_prop_with_empty_value(e)
                            clean_list.append(clean_e)
                        final_expect_value[k] = clean_list
        return final_expect_value

    @abstractmethod
    def _expected_serialize_value(self) -> dict:
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


_TEST_DATA: List[tuple] = []


def _set_test_data(
    is_valid: bool, data_model: Union[str, tuple], opt_globals_callback: Optional[Callable] = None
) -> None:
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
    path = [
        str(pathlib.Path(__file__).parent.parent.parent.parent),
        "data",
        "check_test",
        "data_model",
        f"{config_type}",
        "*.yaml",
    ]
    insert_index = path.index(f"{config_type}")
    if isinstance(data_model, tuple):
        for dm in data_model:
            path.insert(insert_index, dm)
            insert_index += 1
    else:
        assert isinstance(data_model, str), f"If parameter *data_model* is not *tuple* type, it must be *str* type."
        path.insert(insert_index, data_model)
    path = tuple(path)
    yaml_dir = os.path.join(*path)
    for yaml_config_path in glob.glob(yaml_dir):
        global_var_operation((yaml_config_path, expected_is_work))


def set_checking_test_data(
    data_modal_dir: Union[str, tuple],
    reset: bool = True,
    reset_callback: Optional[Callable] = None,
    opt_globals_callback: Optional[Callable] = None,
) -> None:
    if reset:
        reset_callback() if reset_callback else reset_test_data()
    init_checking_test_data(data_modal_dir, opt_globals_callback)


def init_checking_test_data(data_modal_dir: Union[str, tuple], opt_globals_callback: Optional[Callable] = None) -> None:
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
        self._test_is_work_process(sut_with_nothing, test_data_path, criteria)

    def _test_is_work_process(self, sut_with_nothing: _Config, test_data_path: str, criteria: bool) -> None:
        data_model = sut_with_nothing.deserialize(data=YAML().read(path=test_data_path))
        if data_model is not None:  # For data modal *BaseConfig*
            assert isinstance(data_model, _Config) and isinstance(data_model, _Checkable)
            data_model.stop_if_fail = False
            is_valid_to_work = data_model.is_work()
            assert is_valid_to_work is criteria


class HasItemsPropConfigTestSuite(ConfigTestSpec, ABC):

    @pytest.mark.parametrize(
        "items_data",
        [
            # Miss columns
            [
                {"name": "id", "required": True, "type": "str"},
                {"name": "name", "required": True, "type": "str"},
            ],
            # Have columns it doesn't have
            [
                {"name": "id", "required": True, "type": "str"},
                {"name": "name", "required": True, "type": "str"},
                {"name": "what_is_this", "required": True, "type": "str"},
            ],
            # Details in property *items* are different
            [
                {"name": "id", "required": True, "type": "str"},
                {"name": "name", "required": True, "type": "str"},
                {"name": "project", "required": False, "type": "list", "items": [{"required": True, "type": "str"}]},
                {
                    "name": "responsibility",
                    "required": True,
                    "type": "list",
                    "items": [
                        {"name": "project", "required": True, "type": "str"},
                        {
                            "name": "language",
                            "required": True,
                            "type": "list",
                            "items": [{"required": True, "type": "str"}],
                        },
                    ],
                },
            ],
            # Details in property *items.items* are different
            [
                {"name": "id", "required": True, "type": "str"},
                {"name": "name", "required": True, "type": "str"},
                {"name": "project", "required": True, "type": "list", "items": [{"required": True, "type": "int"}]},
                {
                    "name": "responsibility",
                    "required": True,
                    "type": "list",
                    "items": [
                        {"name": "project", "required": True, "type": "str"},
                        {
                            "name": "language",
                            "required": True,
                            "type": "list",
                            "items": [{"required": True, "type": "str"}],
                        },
                    ],
                },
            ],
        ],
    )
    def test_compare_with_other_has_different_nested_element(self, items_data: List[dict]):
        constructor = self._data_model_constructor
        constructor["items"] = [
            {"name": "id", "required": True, "type": "str"},
            {"name": "name", "required": True, "type": "str"},
            {"name": "project", "required": True, "type": "list", "items": [{"required": True, "type": "str"}]},
            {
                "name": "responsibility",
                "required": True,
                "type": "list",
                "items": [
                    {"name": "project", "required": True, "type": "str"},
                    {
                        "name": "language",
                        "required": True,
                        "type": "list",
                        "items": [{"required": True, "type": "str"}],
                    },
                ],
            },
        ]
        item = self._data_model_not_instantiate_yet(**constructor)

        diff_constructor = constructor
        diff_constructor["items"] = items_data
        diff_item = self._data_model_not_instantiate_yet(**diff_constructor)

        assert item != diff_item

    @property
    @abstractmethod
    def _data_model_not_instantiate_yet(self) -> Type[_HasItemsPropConfig]:
        pass

    @property
    @abstractmethod
    def _data_model_constructor(self) -> dict:
        pass


class HasFormatPropConfigTestSuite(metaclass=ABCMeta):

    @pytest.mark.parametrize(
        ("value_format", "data_type", "default", "expect_value"),
        [
            (None, None, None, "no default"),
            (None, None, "some default", "some default"),
            (Format(strategy=FormatStrategy.BY_DATA_TYPE), str, "", str),
            (Format(strategy=FormatStrategy.BY_DATA_TYPE), int, "", int),
            (Format(strategy=FormatStrategy.BY_DATA_TYPE), "big_decimal", "", Decimal),
            (Format(strategy=FormatStrategy.BY_DATA_TYPE), bool, "", bool),
            (Format(strategy=FormatStrategy.FROM_ENUMS, enums=["ENUM_1", "ENUM_2"]), str, "", ["ENUM_1", "ENUM_2"]),
            (
                Format(
                    strategy=FormatStrategy.CUSTOMIZE,
                    customize="<test_var>",
                    variables=[
                        Variable(name="test_var", value_format=ValueFormat.String, digit=None, size=None, enum=None)
                    ],
                ),
                str,
                "",
                str,
            ),
            (
                Format(
                    strategy=FormatStrategy.CUSTOMIZE,
                    customize="<test_var>",
                    variables=[
                        Variable(name="test_var", value_format=ValueFormat.Integer, digit=None, size=None, enum=None)
                    ],
                ),
                str,
                "",
                str,
            ),
            (
                Format(
                    strategy=FormatStrategy.CUSTOMIZE,
                    customize="<test_var>",
                    variables=[
                        Variable(name="test_var", value_format=ValueFormat.BigDecimal, digit=None, size=None, enum=None)
                    ],
                ),
                str,
                "",
                str,
            ),
            (
                Format(
                    strategy=FormatStrategy.CUSTOMIZE,
                    customize="<test_var>",
                    variables=[
                        Variable(name="test_var", value_format=ValueFormat.Boolean, digit=None, size=None, enum=None)
                    ],
                ),
                str,
                "",
                str,
            ),
            (
                Format(
                    strategy=FormatStrategy.CUSTOMIZE,
                    customize="<test_var>",
                    variables=[
                        Variable(
                            name="test_var",
                            value_format=ValueFormat.Enum,
                            digit=None,
                            size=None,
                            enum=["VALUE_ENUM_1", "VALUE_ENUM_2"],
                        )
                    ],
                ),
                str,
                "",
                ["VALUE_ENUM_1", "VALUE_ENUM_2"],
            ),
        ],
    )
    def test_generate_value_by_format(
        self, value_format: Format, data_type: Union[str, object], default: str, expect_value: Union[str, list, type]
    ) -> None:
        formatter = self._data_model_not_instantiate_yet()
        assert hasattr(formatter, "value_type")
        setattr(formatter, "value_type", data_type)
        logger.debug(f"formatter: {getattr(formatter, 'value_type')}")
        formatter.value_format = value_format
        kwarg = {"data_type": data_type, "default": default} if default else {"data_type": data_type}
        value = formatter.generate_value_by_format(**kwarg)
        if isinstance(expect_value, str):
            assert value == expect_value
        elif isinstance(expect_value, list):
            assert value in expect_value
        else:
            assert isinstance(value, expect_value)

    @property
    @abstractmethod
    def _data_model_not_instantiate_yet(self) -> Type[_HasFormatPropConfig]:
        pass


TestDividingData = namedtuple(
    "TestDividingData",
    (
        "should_divide",
        "dry_run",
        "tag_directory_exist",
        "should_check_dir_exist",
        "should_run_mkdir",
        "should_run_serialize",
    ),
)


class DividableTestSuite(ConfigTestSpec, ABC):
    @pytest.mark.parametrize(
        "test_data",
        [
            TestDividingData(
                should_divide=False,
                dry_run=True,
                tag_directory_exist=True,
                should_check_dir_exist=False,
                should_run_mkdir=False,
                should_run_serialize=True,
            ),
            TestDividingData(
                should_divide=False,
                dry_run=False,
                tag_directory_exist=True,
                should_check_dir_exist=False,
                should_run_mkdir=False,
                should_run_serialize=True,
            ),
            TestDividingData(
                should_divide=False,
                dry_run=True,
                tag_directory_exist=False,
                should_check_dir_exist=False,
                should_run_mkdir=False,
                should_run_serialize=True,
            ),
            TestDividingData(
                should_divide=False,
                dry_run=False,
                tag_directory_exist=False,
                should_check_dir_exist=False,
                should_run_mkdir=False,
                should_run_serialize=True,
            ),
            TestDividingData(
                should_divide=True,
                dry_run=True,
                tag_directory_exist=False,
                should_check_dir_exist=False,
                should_run_mkdir=False,
                should_run_serialize=False,
            ),
            TestDividingData(
                should_divide=True,
                dry_run=True,
                tag_directory_exist=True,
                should_check_dir_exist=False,
                should_run_mkdir=False,
                should_run_serialize=False,
            ),
            TestDividingData(
                should_divide=True,
                dry_run=False,
                tag_directory_exist=False,
                should_check_dir_exist=True,
                should_run_mkdir=True,
                should_run_serialize=True,
            ),
            TestDividingData(
                should_divide=True,
                dry_run=False,
                tag_directory_exist=True,
                should_check_dir_exist=True,
                should_run_mkdir=False,
                should_run_serialize=True,
            ),
        ],
    )
    def test_dividing_serialize(self, test_data: TestDividingData, sut: _Config):
        self._test_dividing_serialize_process(test_data=test_data, sut=sut)

    def _test_dividing_serialize_process(self, test_data: TestDividingData, sut: _Config) -> None:
        def _get_abs_module(_obj: object) -> str:
            return f"{_obj.__module__}.{_obj.__class__.__name__}"

        assert isinstance(sut, _Config) and isinstance(sut, TemplatableConfigDividable)
        assert isinstance(self._lower_layer_data_modal_for_divide, _Config) and isinstance(
            self._lower_layer_data_modal_for_divide, BeDividedableAsTemplatableConfig
        )

        # Given
        with patch(f"{_get_abs_module(sut)}.should_divide", new_callable=PropertyMock) as mock_should_divide:
            mock_should_divide.return_value = test_data.should_divide
            with patch(
                f"{_get_abs_module(self._lower_layer_data_modal_for_divide)}.api_name", new_callable=PropertyMock
            ) as mock_prop_api_name:
                mock_prop_api_name.return_value = "test_config"
                with patch(
                    f"{_get_abs_module(self._lower_layer_data_modal_for_divide)}.tag", new_callable=PropertyMock
                ) as mock_prop_tag:
                    mock_prop_tag.return_value = "pytest-mocked-api"
                    with patch("pymock_api.model.api_config.template._divide.YAML.write") as mock_yaml_write:
                        with patch.object(sut, "serialize_lower_layer") as mock_serialize_lower_layer:
                            with patch(
                                "os.path.exists", return_value=test_data.tag_directory_exist
                            ) as mock_check_file_exist:
                                with patch("os.mkdir") as mock_mkdir:
                                    # When: Run target function
                                    sut.dry_run = test_data.dry_run
                                    sut.dividing_serialize(
                                        data=self._lower_layer_data_modal_for_divide,
                                    )

                                    # Should: Verify
                                    mock_should_divide.assert_called_once()
                                    if test_data.should_check_dir_exist:
                                        mock_check_file_exist.assert_called_once()
                                    else:
                                        mock_check_file_exist.assert_not_called()
                                    if test_data.should_run_mkdir:
                                        mock_mkdir.assert_called_once()
                                    else:
                                        mock_mkdir.assert_not_called()
                                    if test_data.should_run_serialize:
                                        mock_serialize_lower_layer.assert_called_once()
                                    else:
                                        mock_serialize_lower_layer.assert_not_called()
                                    if test_data.should_check_dir_exist and test_data.should_run_serialize:
                                        mock_yaml_write.assert_called_once()
                                    else:
                                        mock_yaml_write.assert_not_called()

    @property
    @abstractmethod
    def _lower_layer_data_modal_for_divide(self) -> _Config:
        pass
