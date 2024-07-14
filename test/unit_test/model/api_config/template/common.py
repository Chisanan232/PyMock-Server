import copy
import re
from typing import Any, List, Union

import pytest

from pymock_api.model.api_config.template.common import (
    TemplateFormatConfig,
    TemplateFormatEntity,
)
from pymock_api.model.api_config.variable import Variable

from ....._values import (
    _Customize_Format,
    _Customize_Format_With_Self_Vars,
    _General_Enum_Format,
    _General_Format,
    _Mock_Template_Common_Config_Format_Config,
    _Mock_Template_Common_Config_Format_Entity,
    _Test_Variables_BigDecimal_TWD,
    _Test_Variables_BigDecimal_USD,
    _Test_Variables_Currency_Code,
)
from .._base import (
    CheckableTestSuite,
    ConfigTestSpec,
    _assertion_msg,
    set_checking_test_data,
)


class TestTemplateFormatEntity(ConfigTestSpec):

    @pytest.fixture(scope="function")
    def sut(self) -> TemplateFormatEntity:
        return TemplateFormatEntity(
            name=_Mock_Template_Common_Config_Format_Entity["name"],
            config=_Mock_Template_Common_Config_Format_Entity["config"],
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> TemplateFormatEntity:
        return TemplateFormatEntity()

    def test_value_attributes(self, sut: TemplateFormatEntity):
        assert sut.name == _Mock_Template_Common_Config_Format_Entity["name"], _assertion_msg
        assert sut.config.serialize() == self._clean_prop_with_empty_value(
            _Mock_Template_Common_Config_Format_Entity["config"]
        ), _assertion_msg

    def _expected_serialize_value(self) -> Any:
        return _Mock_Template_Common_Config_Format_Entity

    def _expected_deserialize_value(self, obj: TemplateFormatEntity) -> None:
        assert isinstance(obj, TemplateFormatEntity)
        assert obj.name == _Mock_Template_Common_Config_Format_Entity["name"]
        assert obj.config.serialize() == self._clean_prop_with_empty_value(
            _Mock_Template_Common_Config_Format_Entity["config"]
        )

    @pytest.mark.parametrize("invalid_name", [None, ""])
    def test_deserialize_with_invalid(self, invalid_name: str):
        with pytest.raises(ValueError):
            TemplateFormatEntity().deserialize({"name": invalid_name})


class TestTemplateFormatConfig(CheckableTestSuite):
    test_data_dir = ("template_sections", "template_common_config", "template_format")
    set_checking_test_data(test_data_dir)

    @pytest.fixture(scope="function")
    def sut(self) -> TemplateFormatConfig:
        return TemplateFormatConfig(
            entities=_Mock_Template_Common_Config_Format_Config["entities"],
            variables=_Mock_Template_Common_Config_Format_Config["variables"],
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> TemplateFormatConfig:
        return TemplateFormatConfig()

    def test_value_attributes(self, sut: TemplateFormatConfig):
        self._verify_element_of_list(sut.entities, "entities")
        self._verify_element_of_list(sut.variables, "variables")

    def test_serialize_with_none(self, sut_with_nothing: TemplateFormatConfig):
        assert sut_with_nothing.serialize() is not None

    def _expected_serialize_value(self) -> Any:
        return _Mock_Template_Common_Config_Format_Config

    def _expected_deserialize_value(self, obj: TemplateFormatConfig) -> None:
        assert isinstance(obj, TemplateFormatConfig)
        self._verify_element_of_list(obj.entities, "entities")
        self._verify_element_of_list(obj.variables, "variables")

    def _verify_element_of_list(self, array: List[Union[TemplateFormatEntity, Variable]], expect_key: str) -> None:
        assert array
        for ele in array:
            assert ele is not None
            expect = list(
                filter(lambda e: e["name"] == ele.name, _Mock_Template_Common_Config_Format_Config[expect_key])
            )
            assert expect
            assert ele.serialize() == self._clean_prop_with_empty_value(expect[0])

    @pytest.mark.parametrize(
        ("entities_data", "variables_data"),
        [
            # Miss columns at section *entities*
            (
                # entities
                [
                    {"name": "general_format", "config": _General_Format},
                    {"name": "general_enum_format", "config": _General_Enum_Format},
                    {"name": "customize_format", "config": _Customize_Format},
                ],
                # variables
                [
                    _Test_Variables_BigDecimal_USD,
                    _Test_Variables_BigDecimal_TWD,
                    _Test_Variables_Currency_Code,
                ],
            ),
            # Miss columns at section *variables*
            (
                # entities
                [
                    {"name": "general_format", "config": _General_Format},
                    {"name": "general_enum_format", "config": _General_Enum_Format},
                    {"name": "customize_format", "config": _Customize_Format},
                    {"name": "customize_format_with_self_vars", "config": _Customize_Format_With_Self_Vars},
                ],
                # variables
                [
                    _Test_Variables_BigDecimal_USD,
                    _Test_Variables_BigDecimal_TWD,
                ],
            ),
            # Have columns it doesn't have at section *entities*
            (
                # entities
                [
                    {"name": "general_format", "config": _General_Format},
                    {"name": "general_enum_format", "config": _General_Enum_Format},
                    {"name": "customize_format", "config": _Customize_Format},
                    {"name": "customize_format_with_self_vars", "config": _Customize_Format_With_Self_Vars},
                    {"name": "what_is_this", "config": _Customize_Format_With_Self_Vars},
                ],
                # variables
                [
                    _Test_Variables_BigDecimal_USD,
                    _Test_Variables_BigDecimal_TWD,
                    _Test_Variables_Currency_Code,
                ],
            ),
            # Have columns it doesn't have at section *variables*
            (
                # entities
                [
                    {"name": "general_format", "config": _General_Format},
                    {"name": "general_enum_format", "config": _General_Enum_Format},
                    {"name": "customize_format", "config": _Customize_Format},
                    {"name": "customize_format_with_self_vars", "config": _Customize_Format_With_Self_Vars},
                ],
                # variables
                [
                    _Test_Variables_BigDecimal_USD,
                    _Test_Variables_BigDecimal_TWD,
                    _Test_Variables_Currency_Code,
                    {
                        "name": "what_is_this",
                        "value_format": "big_decimal",
                        "digit": {
                            "integer": 30,
                            "decimal": 0,
                        },
                        "size": None,
                        "enum": None,
                    },
                ],
            ),
            # Have different columns at section *entities*
            (
                # entities
                [
                    {"name": "general_format", "config": _General_Format},
                    {"name": "general_enum_format", "config": _General_Enum_Format},
                    {"name": "customize_format", "config": _Customize_Format_With_Self_Vars},
                    {"name": "customize_format_with_self_vars", "config": _Customize_Format_With_Self_Vars},
                ],
                # variables
                [
                    _Test_Variables_BigDecimal_USD,
                    _Test_Variables_BigDecimal_TWD,
                    _Test_Variables_Currency_Code,
                ],
            ),
            # Have different columns at section *variables*
            (
                # entities
                [
                    {"name": "general_format", "config": _General_Format},
                    {"name": "general_enum_format", "config": _General_Enum_Format},
                    {"name": "customize_format", "config": _Customize_Format},
                    {"name": "customize_format_with_self_vars", "config": _Customize_Format_With_Self_Vars},
                ],
                # variables
                [
                    _Test_Variables_BigDecimal_USD,
                    _Test_Variables_BigDecimal_TWD,
                    {
                        "name": "currency_code",
                        "value_format": "enum",
                        "digit": None,
                        "size": None,
                        "enum": ["TWD", "USD", "EUR", "JPY", "KRW"],
                    },
                ],
            ),
        ],
    )
    def test_compare_with_other_has_different_element(self, entities_data: List[dict], variables_data: List[dict]):
        constructor: dict = _Mock_Template_Common_Config_Format_Config
        item = TemplateFormatConfig(**constructor)

        diff_constructor = copy.copy(constructor)
        diff_constructor["entities"] = entities_data
        diff_constructor["variables"] = variables_data
        diff_item = TemplateFormatConfig(**diff_constructor)

        assert item != diff_item

    def test_cannot_serialize_with_invalid_element_of_entities(self):
        with pytest.raises(TypeError) as exc_info:
            TemplateFormatConfig(entities="invalid value")
        assert re.search(
            r".{0,32}key \*entities\*.{0,32}be 'dict' or '" + re.escape(TemplateFormatEntity.__name__) + r"'.{0,32}",
            str(exc_info.value),
            re.IGNORECASE,
        )

    def test_cannot_serialize_with_invalid_element_of_variables(self):
        with pytest.raises(TypeError) as exc_info:
            TemplateFormatConfig(variables="invalid value")
        assert re.search(
            r".{0,32}key \*variables\*.{0,32}be 'dict' or '" + re.escape(Variable.__name__) + r"'.{0,32}",
            str(exc_info.value),
            re.IGNORECASE,
        )
