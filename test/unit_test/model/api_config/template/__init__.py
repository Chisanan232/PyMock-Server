from abc import ABC, abstractmethod
from typing import Type

import pytest

from pymock_api.model.api_config import _TemplatableConfig
from pymock_api.model.api_config.template import TemplateSetting

from ....._values import _Mock_Templatable_Setting
from .._base import ConfigTestSpec


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
