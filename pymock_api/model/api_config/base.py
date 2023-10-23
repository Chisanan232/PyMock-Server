from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from ._base import _Config


@dataclass(eq=False)
class BaseConfig(_Config):
    """*The **base** section in **mocked_apis***"""

    url: str = field(default_factory=str)

    def _compare(self, other: "BaseConfig") -> bool:
        return self.url == other.url

    def serialize(self, data: Optional["BaseConfig"] = None) -> Optional[Dict[str, Any]]:
        url: str = self._get_prop(data, prop="url")
        if not url:
            return None
        return {
            "url": url,
        }

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["BaseConfig"]:
        """Convert data to **BaseConfig** type object.

        The data structure should be like following:

        * Example data:
        .. code-block:: python

            {
                'base': {
                    'url': '/test/v1'
                },
            }

        Args:
            data (Dict[str, Any]): Target data to convert.

        Returns:
            A **BaseConfig** type object.

        """
        self.url = data.get("url", None)
        return self

    def is_work(self) -> bool:
        # TODO: Check the path format
        return True
