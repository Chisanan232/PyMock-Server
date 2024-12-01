from abc import ABC, abstractmethod
from typing import Type

import pytest

from pymock_api.model.api_config import _Config
from pymock_api.model.api_config.template.file import TemplateConfigPathSetting

from .._base import ConfigTestSpec


class HasDefaultValueTestSuite(ConfigTestSpec, ABC):

    def test_deserialize_with_invalid_data(self, sut_with_nothing: _Config):
        assert sut_with_nothing.deserialize(data={}) == sut_with_nothing


class TemplateSettingTestSuite(HasDefaultValueTestSuite, ABC):
    @property
    @abstractmethod
    def under_test_data(self) -> dict:
        pass

    @property
    @abstractmethod
    def sut_object(self) -> Type[TemplateConfigPathSetting]:
        pass

    @pytest.fixture(scope="function")
    def sut(self) -> TemplateConfigPathSetting:
        args = {
            "config_path_format": self.under_test_data["config_path_format"],
        }
        return self.sut_object(**args)

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> TemplateConfigPathSetting:
        return self.sut_object()

    def test_eq_operation_with_valid_object(
        self, sut: TemplateConfigPathSetting, sut_with_nothing: TemplateConfigPathSetting
    ):
        sut.config_path_format = "**-tmp"
        super().test_eq_operation_with_valid_object(sut, sut_with_nothing)

    def test_serialize_with_none(self, sut_with_nothing: TemplateConfigPathSetting):
        assert sut_with_nothing.serialize() is not None
        assert sut_with_nothing.config_path_format == self.under_test_data["config_path_format"]

    def test_value_attributes(self, sut: TemplateConfigPathSetting):
        assert sut.config_path_format == self.under_test_data["config_path_format"]

    def _expected_serialize_value(self) -> dict:
        return self.under_test_data

    def _expected_deserialize_value(self, obj: TemplateConfigPathSetting) -> None:
        assert isinstance(obj, self.sut_object)
        assert obj.config_path_format == self.under_test_data["config_path_format"]
