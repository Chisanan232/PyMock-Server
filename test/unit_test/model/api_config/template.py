from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Type
from unittest.mock import MagicMock, Mock, call

import pytest

from pymock_api.model.api_config import TemplateConfig, _Config, _TemplatableConfig
from pymock_api.model.api_config.template import (
    LoadConfig,
    TemplateAPI,
    TemplateApply,
    TemplateConfigLoadable,
    TemplateConfigLoader,
    TemplateConfigOpts,
    TemplateHTTP,
    TemplateRequest,
    TemplateResponse,
    TemplateSetting,
    TemplateValues,
)
from pymock_api.model.enums import ConfigLoadingOrder, set_loading_function

from ...._values import (
    _Mock_Base_File_Path,
    _Mock_Load_Config,
    _Mock_Templatable_Setting,
    _Mock_Template_API_Request_Setting,
    _Mock_Template_API_Response_Setting,
    _Mock_Template_API_Setting,
    _Mock_Template_Apply_Has_Tag_Setting,
    _Mock_Template_Config_Activate,
    _Mock_Template_HTTP_Setting,
    _Mock_Template_Setting,
    _Mock_Template_Values_Setting,
)
from ._base import (
    MOCK_MODEL,
    CheckableTestSuite,
    ConfigTestSpec,
    set_checking_test_data,
)


class TestLoadConfig(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> LoadConfig:
        return LoadConfig(
            includes_apis=_Mock_Load_Config["includes_apis"],
            order=_Mock_Load_Config["order"],
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> LoadConfig:
        return LoadConfig()

    def test_serialize_with_none(self, sut_with_nothing: LoadConfig):
        assert sut_with_nothing.serialize() is not None
        serialized_data = sut_with_nothing.serialize()
        assert serialized_data["includes_apis"] is True
        assert serialized_data["order"] == [o.value for o in getattr(sut_with_nothing, "_default_order")]

    def test_value_attributes(self, sut: LoadConfig):
        assert sut.includes_apis == _Mock_Load_Config["includes_apis"]
        assert [o.value for o in sut.order] == _Mock_Load_Config["order"]

    def _expected_serialize_value(self) -> dict:
        return _Mock_Load_Config

    def _expected_deserialize_value(self, obj: LoadConfig) -> None:
        assert isinstance(obj, LoadConfig)
        assert obj.includes_apis == _Mock_Load_Config["includes_apis"]
        assert [o.value for o in obj.order] == _Mock_Load_Config["order"]


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
            "config_path_format": self.under_test_data["config_path_format"],
        }
        return self.sut_object(**args)

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> TemplateSetting:
        return self.sut_object()

    def test_eq_operation_with_valid_object(self, sut: TemplateSetting, sut_with_nothing: TemplateSetting):
        sut.config_path_format = "**-tmp"
        super().test_eq_operation_with_valid_object(sut, sut_with_nothing)

    def test_serialize_with_none(self, sut_with_nothing: TemplateSetting):
        assert sut_with_nothing.serialize() is not None
        assert sut_with_nothing.config_path_format == self.under_test_data["config_path_format"]

    def test_value_attributes(self, sut: TemplateSetting):
        assert sut.config_path_format == self.under_test_data["config_path_format"]

    def _expected_serialize_value(self) -> dict:
        return self.under_test_data

    def _expected_deserialize_value(self, obj: TemplateSetting) -> None:
        assert isinstance(obj, self.sut_object)
        assert obj.config_path_format == self.under_test_data["config_path_format"]


class TestTemplateAPI(TemplateSettingTestSuite):
    @property
    def under_test_data(self) -> dict:
        return _Mock_Template_API_Setting

    @property
    def sut_object(self) -> Type[TemplateSetting]:
        return TemplateAPI


class TestTemplateHTTP(TemplateSettingTestSuite):
    @property
    def under_test_data(self) -> dict:
        return _Mock_Template_HTTP_Setting

    @property
    def sut_object(self) -> Type[TemplateHTTP]:
        return TemplateHTTP


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
            base_file_path=_Mock_Base_File_Path,
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
        assert sut.base_file_path == _Mock_Base_File_Path
        assert sut.api == MOCK_MODEL.template_values_api
        assert sut.request == MOCK_MODEL.template_values_request
        assert sut.response == MOCK_MODEL.template_values_response

    def test_serialize_with_none(self, sut_with_nothing: TemplateValues):
        sut_with_nothing.base_file_path = None
        sut_with_nothing.api = None
        sut_with_nothing.request = None
        sut_with_nothing.response = None
        super().test_serialize_with_none(sut_with_nothing)

    def _expected_serialize_value(self) -> dict:
        return _Mock_Template_Values_Setting

    def _expected_deserialize_value(self, obj: TemplateValues) -> None:
        assert isinstance(obj, TemplateValues)
        assert obj.base_file_path == _Mock_Base_File_Path
        assert obj.api.serialize() == _Mock_Template_Values_Setting.get("api")
        assert obj.request.serialize() == _Mock_Template_Values_Setting.get("request")
        assert obj.response.serialize() == _Mock_Template_Values_Setting.get("response")


class TestTemplateApply(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> TemplateApply:
        return TemplateApply(
            api=_Mock_Template_Apply_Has_Tag_Setting.get("api"),
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> TemplateApply:
        return TemplateApply()

    def test_value_attributes(self, sut: TemplateApply):
        assert sut.api == _Mock_Template_Apply_Has_Tag_Setting.get("api")

    def test_serialize_with_none(self, sut_with_nothing: TemplateApply):
        serialized_data = sut_with_nothing.serialize()
        assert serialized_data is not None
        assert serialized_data["api"] == []

    def _expected_serialize_value(self) -> dict:
        return _Mock_Template_Apply_Has_Tag_Setting

    def _expected_deserialize_value(self, obj: TemplateApply) -> None:
        assert isinstance(obj, TemplateApply)
        assert obj.api == _Mock_Template_Apply_Has_Tag_Setting.get("api")


class TestTemplateConfig(CheckableTestSuite):
    test_data_dir = "template"
    set_checking_test_data(test_data_dir)

    @pytest.fixture(scope="function")
    def sut(self) -> TemplateConfig:
        return TemplateConfig(
            activate=_Mock_Template_Config_Activate,
            load_config=MOCK_MODEL.template_load_config,
            values=MOCK_MODEL.template_values,
            apply=MOCK_MODEL.template_apply,
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> TemplateConfig:
        return TemplateConfig()

    def test_value_attributes(self, sut: TemplateConfig):
        # Verify properties of section *template*
        assert sut.activate == MOCK_MODEL.template_config.activate

        # Verify section *template.values*
        assert sut.values.api == MOCK_MODEL.template_values_api
        assert sut.values.request == MOCK_MODEL.template_values_request
        assert sut.values.response == MOCK_MODEL.template_values_response

        # Verify section *template.apply*
        assert sut.apply == MOCK_MODEL.template_apply

    def test_serialize_with_none(self, sut_with_nothing: TemplateConfig):
        sut_with_nothing.activate = None
        sut_with_nothing.values = None
        sut_with_nothing.apply = None
        super().test_serialize_with_none(sut_with_nothing)

    def _expected_serialize_value(self) -> dict:
        return _Mock_Template_Setting

    def _expected_deserialize_value(self, obj: TemplateConfig) -> None:
        assert isinstance(obj, TemplateConfig)
        assert obj.activate == _Mock_Template_Setting.get("activate")
        assert obj.values.serialize() == _Mock_Template_Setting.get("values")
        assert obj.apply.serialize() == _Mock_Template_Setting.get("apply")


class LoadConfigFunction(Enum):
    """
    Here values are the function naming of object *TemplateConfigLoadable* which loads configuration
    """

    FROM_DATA: str = "apis:_load_mocked_apis_from_data"
    BY_FILE: str = "file:_load_templatable_config"
    BY_APPLY: str = "apply:_load_templatable_config_by_apply"


class MockTemplateConfigOpts(TemplateConfigOpts):
    _template_config_val = None
    __config_file_format_val = None

    @property
    def _template_config(self) -> TemplateConfig:
        return self._template_config_val

    @_template_config.setter
    def _template_config(self, t: TemplateConfig) -> None:
        self._template_config_val = t

    @property
    def _config_file_format(self) -> str:
        return self.__config_file_format_val

    @_config_file_format.setter
    def _config_file_format(self, k: str) -> None:
        self.__config_file_format_val = k

    @property
    def _deserialize_as_template_config(self) -> "_TemplatableConfig":
        pass

    def _set_template_config(self, config: _Config, **kwargs) -> None:
        pass

    def _set_mocked_apis(self, api_key: str = "", api_config: Optional[_Config] = None) -> None:
        pass


class DummyTemplateLoadableDataModal(TemplateConfigLoader):
    pass


class TestTemplateConfigLoadable:
    @pytest.fixture(scope="class")
    def loadable_data_modal(self) -> TemplateConfigLoadable:
        return DummyTemplateLoadableDataModal()

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
        self,
        loadable_data_modal: TemplateConfigLoadable,
        load_order: List[ConfigLoadingOrder],
        expected_func_run_order: List[LoadConfigFunction],
    ):
        # assert isinstance(sut, TemplateConfigLoadable)
        expected_func_run_order = [func.value.split(":") for func in expected_func_run_order]

        # Parent mock object for mocking target functions
        mock_parent = Mock()
        mock_load_config_data = {}
        # Magic mock the target function
        for func in expected_func_run_order:
            setattr(loadable_data_modal, func[1], MagicMock())
            mock_load_config_data[func[0]] = getattr(loadable_data_modal, func[1])
        # Annotate some functions as magic functions
        for func in expected_func_run_order:
            setattr(mock_parent, func[1], getattr(loadable_data_modal, func[1]))

        # Generate criteria of the function running order
        criteria_order = []
        for func in expected_func_run_order:
            if func[1] == "_load_mocked_apis_from_data":
                criteria = getattr(call, func[1])({})
            else:
                criteria = getattr(call, func[1])()
            criteria_order.append(criteria)

        # Pre-process of setting loading function
        set_loading_function(data_model_key="data_modal", **mock_load_config_data)
        template_config = TemplateConfig(
            activate=True,
            load_config=LoadConfig(includes_apis=True, order=load_order),
        )
        mock_template_config_opts_instance = MockTemplateConfigOpts()
        mock_template_config_opts_instance._template_config = template_config
        mock_template_config_opts_instance._config_file_format = "data_modal"

        loadable_data_modal._template_config_opts = mock_template_config_opts_instance

        # Run the target function
        loadable_data_modal.load_config({})

        # Verify the running result
        mock_parent.assert_has_calls(criteria_order)
