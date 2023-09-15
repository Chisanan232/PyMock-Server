from typing import Any, Dict, Optional, Union

from ..._utils import YAML
from ..._utils.file_opt import _BaseFileOperation
from ...model import MockAPIs
from ._base import _Config


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
