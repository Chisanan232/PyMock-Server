from abc import ABC
from dataclasses import dataclass

from fake_api_server.model.api_config._base import _Config

from ._base import _BaseTemplatableConfig
from ._divide import BeDividedableAsTemplatableConfig, TemplatableConfigDividable
from ._load.process import TemplatableConfigLoadable


class _OperatingTemplatableConfig(_Config, TemplatableConfigLoadable, TemplatableConfigDividable):
    """
    Only operations of templatable configuration, e.g., loading the templatable configuration or divide the templatable
    configuration.
    """


@dataclass(eq=False)
class _GeneralTemplatableConfig(
    _BaseTemplatableConfig, TemplatableConfigLoadable, TemplatableConfigDividable, BeDividedableAsTemplatableConfig, ABC
):
    """
    Mostly same as *_OperatingTemplatableConfig*, but it also overrides the major methods *serialize* and *deserialize*.
    """


@dataclass(eq=False)
class _DividableOnlyTemplatableConfig(_BaseTemplatableConfig, BeDividedableAsTemplatableConfig, ABC):
    """
    Mostly same as *_GeneralTemplatableConfig*, but it only could be divided by other data modals which could divide
    templatable configuration.
    """
