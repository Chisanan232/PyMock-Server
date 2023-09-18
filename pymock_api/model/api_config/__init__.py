"""*The data objects of configuration*

content ...
"""
from typing import Any, Dict, List, Optional, Union

from ..._utils import YAML
from ..._utils.file_opt import _BaseFileOperation
from ._base import _Config, _TemplatableConfig
from .apis import (
    HTTP,
    APIParameter,
    HTTPRequest,
    HTTPResponse,
    MockAPI,
    ResponseProperty,
)
from .base import BaseConfig
from .item import IteratorItem
from .template import TemplateConfig


class MockAPIs(_Config):
    """*The **mocked_apis** section*"""

    _template: TemplateConfig
    _base: Optional[BaseConfig]
    _apis: Dict[str, Optional[MockAPI]]

    _need_template_in_config: bool = True

    def __init__(
        self,
        template: Optional[TemplateConfig] = None,
        base: Optional[BaseConfig] = None,
        apis: Dict[str, Optional[MockAPI]] = {},
    ):
        self._template = TemplateConfig() if template is None else template
        self._base = base
        self._apis = apis

    def __len__(self):
        return len(self.apis.keys())

    def _compare(self, other: "MockAPIs") -> bool:
        return self.base == other.base and self.apis == other.apis

    @property
    def template(self) -> TemplateConfig:
        return self._template

    @template.setter
    def template(self, template: Union[dict, TemplateConfig]) -> None:
        if template:
            if isinstance(template, dict):
                self._template = TemplateConfig().deserialize(data=template)
            elif isinstance(template, TemplateConfig):
                self._template = template
            else:
                raise TypeError("Setter *MockAPIs.template* only accepts dict or TemplateConfig type object.")

    @property
    def base(self) -> Optional[BaseConfig]:
        return self._base

    @base.setter
    def base(self, base: Union[dict, BaseConfig]) -> None:
        if base:
            if isinstance(base, dict):
                self._base = BaseConfig().deserialize(data=base)
            elif isinstance(base, BaseConfig):
                self._base = base
            else:
                raise TypeError("Setter *MockAPIs.base* only accepts dict or BaseConfig type object.")
        else:
            self._base = None

    @property
    def apis(self) -> Dict[str, Optional[MockAPI]]:
        return self._apis

    @apis.setter
    def apis(self, apis: Dict[str, Union[dict, MockAPI]]) -> None:
        if apis:
            if not isinstance(apis, dict):
                raise TypeError("Setter *MockAPIs.apis* only accepts dict or MockAPI type object.")

            ele_types = set(list(map(lambda v: isinstance(v, MockAPI), apis.values())))
            if len(ele_types) != 1:
                raise ValueError("It has multiple types of the data content. Please unify these objects data type.")

            if False in ele_types:
                self._apis = {}
                for api_name, api_config in apis.items():
                    self._apis[api_name] = MockAPI().deserialize(data=(api_config or {}))
            else:
                self._apis = apis  # type: ignore
        else:
            self._apis = {}

    @property
    def set_template_in_config(self) -> bool:
        return self._need_template_in_config

    @set_template_in_config.setter
    def set_template_in_config(self, _set: bool) -> None:
        self._need_template_in_config = _set

    def serialize(self, data: Optional["MockAPIs"] = None) -> Optional[Dict[str, Any]]:
        template = (data.template if data else None) or self.template
        base = (data.base if data else None) or self.base
        apis = (data.apis if data else None) or self.apis
        if not (base and apis):
            return None

        # Process section *base*
        api_info = {  # type: ignore[var-annotated]
            "base": BaseConfig().serialize(data=base),
            "apis": {},
        }
        if self._need_template_in_config:
            api_info["template"] = template.serialize()

        # Process section *apis*
        all_mocked_apis = {}
        for api_name, api_config in apis.items():
            all_mocked_apis[api_name] = MockAPI().serialize(data=api_config)
        api_info["apis"] = all_mocked_apis

        return api_info

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["MockAPIs"]:
        """Convert data to **MockAPIs** type object.

        The data structure should be like following:

        * Example data:
        .. code-block:: python

            {
                'base': {'url': '/test/v1'},
                'apis': {
                    'google_home': {
                        'url': '/google',
                        'http': {
                            'request': {
                                'method': 'GET',
                                'parameters': [{'param1': 'val1'}]
                            },
                            'response': {
                                'value': 'This is Google home API.'
                            }
                        }
                    },
                    'test_home': {
                        'url': '/google',
                        'http': {
                            'request': {
                                'method': 'GET',
                                'parameters': [{'param1': 'val1'}]
                            },
                            'response': {
                                'value': '{ "responseCode": "200", "errorMessage": "OK", "content": "This is Test home." }'
                            }
                        },
                        'cookie': [{'TEST': 'cookie_value'}]
                    },
                    'youtube_home': {
                        'url': '/youtube',
                        'http': {
                            'request': {
                                'method': 'GET',
                                'parameters': [{'param1': 'val1'}]
                            },
                            'response': {'value': 'youtube.json'}
                        },
                        'cookie': [{'USERNAME': 'test'}, {'SESSION_EXPIRED': '2023-12-31T00:00:00.000'}]
                    }
                }
            }

        Args:
            data (Dict[str, Any]): Target data to convert.

        Returns:
            A **MockAPIs** type object.

        """
        # Processing section *template*
        template_info = data.get("template", {})
        if not template_info:
            self._need_template_in_config = False
        self.template = TemplateConfig().deserialize(data=template_info)

        # Processing section *base*
        base_info = data.get("base", None)
        self.base = BaseConfig().deserialize(data=base_info)

        # Processing section *apis*
        mocked_apis_info = data.get("apis", {})
        self.apis = {}
        if mocked_apis_info:
            for mock_api_name in mocked_apis_info.keys():
                self.apis[mock_api_name] = MockAPI().deserialize(data=mocked_apis_info.get(mock_api_name, None))
        # FIXME: This logic should align with the template apply strategy.
        else:
            # Run dividing feature process
            # 1. Use the templatable values set target file paths and list all of them (hint: glob.glob).
            # 2. Read the file and deserialize its content as data model.
            # 3. Set the data model at current object's property.
            # 4. Run step #1 to step #3 again and again until finish reading all files.
            # 5. Extract the core logic as template method to object *TemplatableConfig*.
            pass
        return self

    def get_api_config_by_url(self, url: str, base: Optional[BaseConfig] = None) -> Optional[MockAPI]:
        url = url.replace(base.url, "") if base else url
        for k, v in self._apis.items():
            if v and v.url == url:
                return self._apis[k]
        return None

    def get_all_api_config_by_url(self, url: str, base: Optional[BaseConfig] = None) -> Dict[str, MockAPI]:
        url = url.replace(base.url, "") if base else url
        all_api_configs: Dict[str, MockAPI] = {}
        for k, v in self._apis.items():
            if v and v.url == url:
                all_api_configs[v.http.request.method.upper()] = self._apis[k]  # type: ignore[union-attr,assignment]
        return all_api_configs

    def group_by_url(self) -> Dict[str, List[MockAPI]]:
        apis = self._apis
        aggregated_apis: Dict[str, List[MockAPI]] = {}
        for api_name, api_config in apis.items():
            assert api_config and api_config.url
            one_url_details = aggregated_apis.get(api_config.url, [])
            one_url_details.append(api_config)
            aggregated_apis[api_config.url] = one_url_details
        return aggregated_apis


class APIConfig(_Config):
    """*The entire configuration*"""

    _name: str = ""
    _description: str = ""
    _apis: Optional[MockAPIs]

    _configuration: _BaseFileOperation = YAML()
    _need_template_in_config: bool = True

    def __init__(self, name: str = "", description: str = "", apis: Optional[MockAPIs] = None):
        self._name = name
        self._description = description
        self._apis = apis

    def __len__(self):
        return len(self._apis) if self._apis else 0

    def _compare(self, other: "APIConfig") -> bool:
        return self.name == other.name and self.description == other.description and self.apis == other.apis

    @property
    def _config_operation(self) -> _BaseFileOperation:
        return self._configuration

    def has_apis(self) -> bool:
        return len(self) != 0

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, desc: str) -> None:
        self._description = desc

    @property
    def apis(self) -> Optional[MockAPIs]:
        return self._apis

    @apis.setter
    def apis(self, apis: Union[dict, MockAPIs]) -> None:
        if apis:
            if isinstance(apis, dict):
                self._apis = MockAPIs().deserialize(data=apis)
            elif isinstance(apis, MockAPIs):
                self._apis = apis
            else:
                raise TypeError("Setter *APIConfig.apis* only accepts dict or MockAPIs type object.")
        else:
            self._apis = None

    @property
    def set_template_in_config(self) -> bool:
        return self._need_template_in_config

    @set_template_in_config.setter
    def set_template_in_config(self, _set: bool) -> None:
        self._need_template_in_config = _set

    def serialize(self, data: Optional["APIConfig"] = None) -> Optional[Dict[str, Any]]:
        name = (data.name if data else None) or self.name
        description = (data.description if data else None) or self.description
        apis = (data.apis if data else None) or self.apis
        if not apis:
            return None
        apis.set_template_in_config = self.set_template_in_config
        return {
            "name": name,
            "description": description,
            "mocked_apis": apis.serialize(),
        }

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["APIConfig"]:
        """Convert data to **APIConfig** type object.

        The data structure should be like following:

        * Example data:
        .. code-block:: python

            {
                'name': 'Test mocked API',
                'description': 'This is a test for the usage demonstration.',
                'mocked_apis': {
                    'base': {'url': '/test/v1'},
                    'apis': {
                        'google_home': {
                            'url': '/google',
                            'http': {
                                'request': {
                                    'method': 'GET',
                                    'parameters': [{'param1': 'val1'}]
                                },
                                'response': {
                                    'value': 'This is Google home API.'
                                }
                            }
                        },
                        'test_home': {
                            'url': '/google',
                            'http': {
                                'request': {
                                    'method': 'GET',
                                    'parameters': [{'param1': 'val1'}]
                                },
                                'response': {
                                    'value': '{
                                        "responseCode": "200", "errorMessage": "OK", "content": "This is Test home."
                                    }'
                                }
                            },
                            'cookie': [{'TEST': 'cookie_value'}]
                        },
                        'youtube_home': {
                            'url': '/youtube',
                            'http': {
                                'request': {
                                    'method': 'GET',
                                    'parameters': [{'param1': 'val1'}]
                                },
                                'response': {'value': 'youtube.json'}
                            },
                            'cookie': [{'USERNAME': 'test'}, {'SESSION_EXPIRED': '2023-12-31T00:00:00.000'}]
                        }
                    }
                }
            }

        Args:
            data (Dict[str, Any]): Target data to convert.

        Returns:
            A **APIConfig** type object.

        """
        self.name = data.get("name", None)
        self.description = data.get("description", None)
        mocked_apis = data.get("mocked_apis", None)
        if mocked_apis:
            mock_apis_data_model = MockAPIs()
            mock_apis_data_model.set_template_in_config = self.set_template_in_config
            self.apis = mock_apis_data_model.deserialize(data=mocked_apis)
        return self

    def from_yaml(self, path: str) -> Optional["APIConfig"]:
        return self.deserialize(data=self._config_operation.read(path))

    def to_yaml(self, path: str) -> None:
        self._config_operation.write(path=path, config=(self.serialize() or {}))
