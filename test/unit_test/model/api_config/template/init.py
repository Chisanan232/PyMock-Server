from enum import Enum
from typing import List, Optional, Type
from unittest.mock import MagicMock, Mock, call

import pytest

from pymock_api.model.api_config import (
    TemplateConfigLoader,
    TemplateFileConfig,
    _BaseTemplatableConfig,
    _BaseTemplateConfigLoader,
    _Config,
)
from pymock_api.model.api_config.template import (
    LoadConfig,
    TemplateApply,
    TemplateConfig,
    TemplateConfigPathAPI,
    TemplateConfigPathHTTP,
    TemplateConfigPathRequest,
    TemplateConfigPathResponse,
    TemplateConfigPathSetting,
    TemplateConfigPathValues,
)
from pymock_api.model.api_config.template._load import (
    TemplateConfigLoaderByApply,
    TemplateConfigLoaderByScanFile,
    TemplateConfigLoaderWithAPIConfig,
    TemplateConfigOpts,
)
from pymock_api.model.enums import (
    ConfigLoadingOrder,
    ConfigLoadingOrderKey,
    set_loading_function,
)

from ....._values import (
    _Mock_Base_File_Path,
    _Mock_Load_Config,
    _Mock_Template_API_Request_Setting,
    _Mock_Template_API_Response_Setting,
    _Mock_Template_API_Setting,
    _Mock_Template_Apply_Has_Tag_Setting,
    _Mock_Template_Config_Activate,
    _Mock_Template_File_Setting,
    _Mock_Template_HTTP_Setting,
    _Mock_Template_Setting,
    _Mock_Template_Values_Setting,
)
from .._base import (
    MOCK_MODEL,
    CheckableTestSuite,
    ConfigTestSpec,
    set_checking_test_data,
)
from . import TemplateSettingTestSuite


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


class TestTemplateConfigPathAPI(TemplateSettingTestSuite):
    @property
    def under_test_data(self) -> dict:
        return _Mock_Template_API_Setting

    @property
    def sut_object(self) -> Type[TemplateConfigPathSetting]:
        return TemplateConfigPathAPI


class TestTemplateConfigPathHTTP(TemplateSettingTestSuite):
    @property
    def under_test_data(self) -> dict:
        return _Mock_Template_HTTP_Setting

    @property
    def sut_object(self) -> Type[TemplateConfigPathHTTP]:
        return TemplateConfigPathHTTP


class TestTemplateConfigPathRequest(TemplateSettingTestSuite):
    @property
    def under_test_data(self) -> dict:
        return _Mock_Template_API_Request_Setting

    @property
    def sut_object(self) -> Type[TemplateConfigPathSetting]:
        return TemplateConfigPathRequest


class TestTemplateConfigPathResponse(TemplateSettingTestSuite):
    @property
    def under_test_data(self) -> dict:
        return _Mock_Template_API_Response_Setting

    @property
    def sut_object(self) -> Type[TemplateConfigPathSetting]:
        return TemplateConfigPathResponse


class TestTemplateConfigPathValues(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> TemplateConfigPathValues:
        return TemplateConfigPathValues(
            base_file_path=_Mock_Base_File_Path,
            api=MOCK_MODEL.template_values_api,
            request=MOCK_MODEL.template_values_request,
            response=MOCK_MODEL.template_values_response,
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> TemplateConfigPathValues:
        return TemplateConfigPathValues()

    def test_eq_operation_with_valid_object(self, sut: _Config, sut_with_nothing: _Config):
        # NOTE: TemplateConfig has default value
        assert sut == sut_with_nothing

    def test_value_attributes(self, sut: TemplateConfigPathValues):
        assert sut.base_file_path == _Mock_Base_File_Path
        assert sut.api == MOCK_MODEL.template_values_api
        assert sut.request == MOCK_MODEL.template_values_request
        assert sut.response == MOCK_MODEL.template_values_response

    def test_serialize_with_none(self, sut_with_nothing: TemplateConfigPathValues):
        sut_with_nothing.base_file_path = None
        sut_with_nothing.api = None
        sut_with_nothing.request = None
        sut_with_nothing.response = None
        super().test_serialize_with_none(sut_with_nothing)

    def _expected_serialize_value(self) -> dict:
        return _Mock_Template_Values_Setting

    def _expected_deserialize_value(self, obj: TemplateConfigPathValues) -> None:
        assert isinstance(obj, TemplateConfigPathValues)
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


class TestTemplateFileConfig(CheckableTestSuite):
    test_data_dir = "file"
    set_checking_test_data(test_data_dir)

    @pytest.fixture(scope="function")
    def sut(self) -> TemplateFileConfig:
        return TemplateFileConfig(
            activate=_Mock_Template_Config_Activate,
            load_config=MOCK_MODEL.template_load_config,
            config_path_values=MOCK_MODEL.template_values,
            apply=MOCK_MODEL.template_apply,
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> TemplateFileConfig:
        return TemplateFileConfig()

    def test_value_attributes(self, sut: TemplateFileConfig):
        # Verify properties of section *template*
        assert sut.activate == MOCK_MODEL.template_file_config.activate

        # Verify section *template.values*
        assert sut.config_path_values.api == MOCK_MODEL.template_values_api
        assert sut.config_path_values.request == MOCK_MODEL.template_values_request
        assert sut.config_path_values.response == MOCK_MODEL.template_values_response

        # Verify section *template.apply*
        assert sut.apply == MOCK_MODEL.template_apply

    def test_serialize_with_none(self, sut_with_nothing: TemplateFileConfig):
        sut_with_nothing.activate = None
        sut_with_nothing.config_path_values = None
        sut_with_nothing.apply = None
        super().test_serialize_with_none(sut_with_nothing)

    def _expected_serialize_value(self) -> dict:
        return _Mock_Template_File_Setting

    def _expected_deserialize_value(self, obj: TemplateFileConfig) -> None:
        assert isinstance(obj, TemplateFileConfig)
        assert obj.activate == _Mock_Template_File_Setting.get("activate")
        assert obj.config_path_values.serialize() == _Mock_Template_File_Setting.get("config_path_values")
        assert obj.apply.serialize() == _Mock_Template_File_Setting.get("apply")


class TestTemplateConfig(CheckableTestSuite):
    test_data_dir = "template_not_yet"
    set_checking_test_data(test_data_dir)

    @pytest.fixture(scope="function")
    def sut(self) -> TemplateConfig:
        return TemplateConfig(
            activate=_Mock_Template_Config_Activate,
            file=MOCK_MODEL.template_file_config,
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> TemplateConfig:
        return TemplateConfig()

    def test_value_attributes(self, sut: TemplateConfig):
        # Verify properties of section *template*
        assert sut.activate == MOCK_MODEL.template_file_config.activate

        # Verify section *template.values*
        assert sut.file.config_path_values.api == MOCK_MODEL.template_values_api
        assert sut.file.config_path_values.request == MOCK_MODEL.template_values_request
        assert sut.file.config_path_values.response == MOCK_MODEL.template_values_response

        # Verify section *template.apply*
        assert sut.file.apply == MOCK_MODEL.template_apply

    def test_serialize_with_none(self, sut_with_nothing: TemplateConfig):
        sut_with_nothing.activate = None
        sut_with_nothing.config_path_values = None
        sut_with_nothing.apply = None
        super().test_serialize_with_none(sut_with_nothing)

    def _expected_serialize_value(self) -> dict:
        return _Mock_Template_Setting

    def _expected_deserialize_value(self, obj: TemplateConfig) -> None:
        assert isinstance(obj, TemplateConfig)
        assert obj.activate == _Mock_Template_Setting.get("activate")
        assert obj.file.serialize() == _Mock_Template_Setting.get("file")


class DummyTemplateConfigLoaderWithAPIConfig(TemplateConfigLoaderWithAPIConfig):
    pass


class DummyTemplateConfigLoaderByScanFile(TemplateConfigLoaderByScanFile):
    pass


class DummyTemplateConfigLoaderByApply(TemplateConfigLoaderByApply):
    pass


class LoadConfigFunction(Enum):
    """
    Here values are the function naming of object *TemplateConfigLoadable* which loads configuration
    """

    FROM_DATA: tuple = ("apis", DummyTemplateConfigLoaderWithAPIConfig)
    BY_FILE: tuple = ("file", DummyTemplateConfigLoaderByScanFile)
    BY_APPLY: tuple = ("apply", DummyTemplateConfigLoaderByApply)


class MockTemplateConfigOpts(TemplateConfigOpts):
    _template_config_val = None
    __config_file_format_val = None

    @property
    def _template_config(self) -> TemplateFileConfig:
        return self._template_config_val

    @_template_config.setter
    def _template_config(self, t: TemplateFileConfig) -> None:
        self._template_config_val = t

    @property
    def _config_file_format(self) -> str:
        return self.__config_file_format_val

    @_config_file_format.setter
    def _config_file_format(self, k: str) -> None:
        self.__config_file_format_val = k

    @property
    def _deserialize_as_template_config(self) -> "_BaseTemplatableConfig":
        pass

    def _set_template_config(self, config: _Config, **kwargs) -> None:
        pass

    def _set_mocked_apis(self, api_key: str = "", api_config: Optional[_Config] = None) -> None:
        pass


class DummyTemplateLoadableDataModal(TemplateConfigLoader):
    def __init__(self):
        super().__init__()
        # Mock the loaders
        self._loaders = {
            ConfigLoadingOrderKey.APIs.value: DummyTemplateConfigLoaderWithAPIConfig(),
            ConfigLoadingOrderKey.FILE.value: DummyTemplateConfigLoaderByScanFile(),
            ConfigLoadingOrderKey.APPLY.value: DummyTemplateConfigLoaderByApply(),
        }


class TestTemplateConfigLoadable:
    @pytest.fixture(scope="class")
    def loadable_data_modal(self) -> _BaseTemplateConfigLoader:
        return DummyTemplateLoadableDataModal()

    @pytest.mark.parametrize(
        ("load_order", "expected_obj_run_order"),
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
        loadable_data_modal: _BaseTemplateConfigLoader,
        load_order: List[ConfigLoadingOrder],
        expected_obj_run_order: List[LoadConfigFunction],
    ):
        # assert isinstance(sut, TemplateConfigLoadable)
        expected_obj_run_order = [func.value for func in expected_obj_run_order]

        # Parent mock object for mocking target functions
        mock_parent = Mock()
        mock_load_config_data = {}
        # Magic mock the target function
        for obj in expected_obj_run_order:
            setattr(obj[1], "load_config", MagicMock())
            mock_load_config_data[obj[0]] = getattr(obj[1], "load_config")
        # Annotate some functions as magic functions
        for obj in expected_obj_run_order:
            setattr(mock_parent, f"{obj[0]}_load_config", getattr(obj[1], "load_config"))

        # Generate criteria of the function running order
        criteria_order = []
        for obj in expected_obj_run_order:
            if obj[0] == "apis":
                criteria = getattr(call, f"{obj[0]}_load_config")({})
            else:
                criteria = getattr(call, f"{obj[0]}_load_config")()
            criteria_order.append(criteria)

        # Pre-process of setting loading function
        set_loading_function(data_model_key="data_modal", **mock_load_config_data)
        template_config = TemplateFileConfig(
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
