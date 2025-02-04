from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from fake_api_server.model.api_config._base import (
    _Checkable,
    _CheckableConfigType,
    _Config,
    _ConfigType,
)
from fake_api_server.model.api_config.format import Format
from fake_api_server.model.api_config.variable import Variable


@dataclass(eq=False)
class TemplateFormatEntity(_Config, _Checkable):

    name: str = field(default_factory=str)
    config: Optional[Format] = None

    def __post_init__(self) -> None:
        if self.config is not None:
            self._convert_config()

    def _convert_config(self):
        if isinstance(self.config, dict):
            self.config = Format().deserialize(self.config)

    def _compare(self, other: "TemplateFormatEntity") -> bool:
        return self.name == other.name and self.config == other.config

    @property
    def key(self) -> str:
        return "entire"

    @_Config._clean_empty_value
    def serialize(self, data: Optional["TemplateFormatEntity"] = None) -> Optional[Dict[str, Any]]:
        name: str = self._get_prop(data, prop="name")
        config: Format = self._get_prop(data, prop="config")
        if not name or not config:
            return None
        serialized_data = {
            "name": name,
            "config": (config.serialize() if config is not None else {}),
        }
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateFormatEntity"]:
        name = data.get("name", None)
        if not name:
            raise ValueError("A format entity must have a name.")
        self.name = name
        self.config = Format().deserialize(data.get("config", {}))
        return self

    def is_work(self) -> bool:
        if not self.props_should_not_be_none(
            under_check={
                f"{self.absolute_model_key}.config": self.config,
            },
            accept_empty=False,
        ):
            return False
        if not self.condition_should_be_true(
            config_key=f"{self.absolute_model_key}.name",
            condition=(self.name is not None and not isinstance(self.name, str)),
        ):
            return False
        assert self.config
        self.config.stop_if_fail = self.stop_if_fail
        return self.config.is_work()


@dataclass(eq=False)
class TemplateFormatConfig(_Config, _Checkable):

    entities: List[TemplateFormatEntity] = field(default_factory=list)
    variables: List[Variable] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.entities is not None and len(self.entities) != 0:
            self._convert_entities()
        if self.variables is not None and len(self.variables) != 0:
            self._convert_variables()

    def _convert_entities(self):
        if False in list(map(lambda i: isinstance(i, (dict, TemplateFormatEntity)), self.entities)):
            raise TypeError(
                f"The data type of key *entities* must be 'dict' or '{TemplateFormatEntity.__name__}' type data."
            )
        self.entities = [TemplateFormatEntity().deserialize(i) if isinstance(i, dict) else i for i in self.entities]

    def _convert_variables(self):
        if False in list(map(lambda i: isinstance(i, (dict, Variable)), self.variables)):
            raise TypeError(f"The data type of key *variables* must be 'dict' or '{Variable.__name__}' type data.")
        self.variables = [Variable().deserialize(i) if isinstance(i, dict) else i for i in self.variables]

    def _compare(self, other: "TemplateFormatConfig") -> bool:

        def find_same_key_format_entity_to_compare_callback(
            self_prop: TemplateFormatEntity, other_prop: TemplateFormatEntity
        ) -> bool:
            return self_prop.name == other_prop.name

        def find_same_key_variable_to_compare_callback(self_prop: Variable, other_prop: Variable) -> bool:
            return self_prop.name == other_prop.name

        return self._compare_array(
            other, "entities", find_same_key_format_entity_to_compare_callback
        ) and self._compare_array(other, "variables", find_same_key_variable_to_compare_callback)

    def _compare_array(
        self,
        other: "TemplateFormatConfig",
        prop: str,
        find_same_key_ele_to_compare_callback: Callable[[_ConfigType, _ConfigType], bool],
    ) -> bool:
        ele_is_same: bool = True

        # Compare the target property size which should be a *list* type value
        self_prop = getattr(self, prop)
        other_prop = getattr(other, prop)
        assert isinstance(self_prop, list)
        assert isinstance(other_prop, list)
        if self_prop and other_prop:
            ele_is_same = len(self_prop) == len(other_prop)

        # Compare target property details
        for ele in self_prop or []:
            same_key_other_ele = list(filter(lambda i: find_same_key_ele_to_compare_callback(ele, i), other_prop or []))
            if not same_key_other_ele:
                ele_is_same = False
                break
            assert len(same_key_other_ele) == 1
            if ele != same_key_other_ele[0]:
                ele_is_same = False
                break

        return ele_is_same

    @property
    def key(self) -> str:
        return "format"

    @_Config._clean_empty_value
    def serialize(self, data: Optional["TemplateFormatConfig"] = None) -> Optional[Dict[str, Any]]:
        serialized_data: Dict[str, list] = {
            "entities": [],
            "variables": [],
        }

        entities: List[TemplateFormatEntity] = self._get_prop(data, prop="entities")
        if entities:
            serialized_data["entities"] = [
                entity.serialize() if isinstance(entity, TemplateFormatEntity) else entity for entity in entities
            ]

        variables: List[Variable] = self._get_prop(data, prop="variables")
        if variables:
            serialized_data["variables"] = [
                variable.serialize() if isinstance(variable, Variable) else variable for variable in variables
            ]
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateFormatConfig"]:

        def _deserialize_entity(entity_data: dict) -> TemplateFormatEntity:
            entity_data_model = TemplateFormatEntity()
            entity_data_model.absolute_model_key = self.key
            return entity_data_model.deserialize(entity_data)

        def _deserialize_variable(variable_data: dict) -> Variable:
            variable_data_model = Variable()
            variable_data_model.absolute_model_key = self.key
            return variable_data_model.deserialize(variable_data)

        self.entities: List[TemplateFormatEntity] = [
            _deserialize_entity(entity) if isinstance(entity, dict) else entity
            for entity in (data.get("entities", []) or [])
        ]

        self.variables: List[Variable] = [
            _deserialize_variable(variable) if isinstance(variable, dict) else variable
            for variable in (data.get("variables", []) or [])
        ]
        return self

    def is_work(self) -> bool:
        # General checking
        assert (
            self.condition_should_be_true(
                config_key=f"{self.absolute_model_key}.entities",
                condition=(
                    len(list(filter(lambda e: isinstance(e, TemplateFormatEntity), self.entities)))
                    != len(self.entities)
                ),
                err_msg=f"The element data type is incorrect at schema key *{self.absolute_model_key}.entities*. Value: {self.entities}",
            )
            is True
        )
        assert (
            self.condition_should_be_true(
                config_key=f"{self.absolute_model_key}.variables",
                condition=(len(list(filter(lambda e: isinstance(e, Variable), self.variables))) != len(self.variables)),
                err_msg=f"The element data type is incorrect at schema key *{self.absolute_model_key}.variables*. Value: {self.variables}",
            )
            is True
        )

        def _i_is_work(i: _CheckableConfigType) -> bool:
            i.stop_if_fail = self.stop_if_fail
            return i.is_work()

        # Checking array type property *entities*
        if self.entities:

            is_work_entities_props = list(filter(lambda i: _i_is_work(i), self.entities))  # type: ignore[var-annotated,arg-type,type-var]
            if len(is_work_entities_props) != len(self.entities):
                return False

        # Checking array type property *variables*
        if self.variables:

            is_work_variables_props = list(filter(lambda i: _i_is_work(i), self.variables))  # type: ignore[var-annotated,arg-type,type-var]
            if len(is_work_variables_props) != len(self.variables):
                return False

        return True

    def get_format(self, name: str) -> Optional[Format]:
        find_result: List[TemplateFormatEntity] = list(filter(lambda e: e.name == name, self.entities))
        if len(find_result) == 0:
            return None
        return find_result[0].config

    def get_variable(self, name: str) -> Optional[Variable]:
        find_result: List[Variable] = list(filter(lambda e: e.name == name, self.variables))
        if len(find_result) == 0:
            return None
        return find_result[0]


@dataclass(eq=False)
class TemplateCommonConfig(_Config, _Checkable):

    activate: bool = field(default=False)
    format: Optional[TemplateFormatConfig] = None

    def __post_init__(self) -> None:
        if self.format is not None:
            self._convert_format()

    def _convert_format(self) -> None:
        if isinstance(self.format, dict):
            self.format = TemplateFormatConfig().deserialize(self.format)

    def _compare(self, other: "TemplateCommonConfig") -> bool:
        return self.activate == other.activate and self.format == other.format

    @property
    def key(self) -> str:
        return "common_config"

    @_Config._clean_empty_value
    def serialize(self, data: Optional["TemplateCommonConfig"] = None) -> Optional[Dict[str, Any]]:
        activate: bool = self.activate or self._get_prop(data, prop="activate")
        template_format: TemplateFormatConfig = self._get_prop(data, prop="format")
        serialized_data: Dict[str, Any] = {
            "activate": activate,
        }
        if template_format:
            serialized_data["format"] = template_format.serialize()
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateCommonConfig"]:
        self.activate = data.get("activate", False)

        template_format_data = data.get("format", {})
        if template_format_data:
            template_format_config = TemplateFormatConfig()
            template_format_config.absolute_model_key = self.key
            self.format = template_format_config.deserialize(template_format_data)
        return self

    def is_work(self) -> bool:
        # General checking
        if not self.props_should_not_be_none(
            under_check={
                f"{self.absolute_model_key}.activate": self.activate,
            },
            accept_empty=False,
        ):
            return False
        if not self.condition_should_be_true(
            config_key=f"{self.absolute_model_key}.activate",
            condition=(not isinstance(self.activate, bool)),
        ):
            return False

        # Checking array type property *format*
        if self.format:
            self.format.stop_if_fail = self.stop_if_fail
            if not self.format.is_work():
                return False
        return True
