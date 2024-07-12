from typing import List

import pytest

from pymock_api.model.api_config.template import TemplateConfig

from ....._values import _Mock_Template_Config_Activate, _Mock_Template_Setting
from .._base import MOCK_MODEL, CheckableTestSuite, set_checking_test_data

_Template_Config_Test_Data: List[tuple] = []


def reset_template_config_test_data() -> None:
    global _Template_Config_Test_Data
    _Template_Config_Test_Data.clear()


def add_template_config_test_data(test_scenario: tuple) -> None:
    global _Template_Config_Test_Data
    _Template_Config_Test_Data.append(test_scenario)


class TestTemplateConfig(CheckableTestSuite):
    test_data_dir = "template"
    set_checking_test_data(
        test_data_dir,
        reset_callback=reset_template_config_test_data,
        opt_globals_callback=add_template_config_test_data,
    )

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
        assert sut.activate == MOCK_MODEL.template_config.activate

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

    @pytest.mark.parametrize(
        ("test_data_path", "criteria"),
        _Template_Config_Test_Data,
    )
    def test_is_work(self, sut_with_nothing: TemplateConfig, test_data_path: str, criteria: bool):
        super().test_is_work(sut_with_nothing, test_data_path, criteria)
