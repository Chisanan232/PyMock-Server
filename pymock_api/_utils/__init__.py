"""*Sub-package for utility functions*"""

from ..model import APIConfig
from .converter import Convert
from .reader import YAMLReader


def load_config(config_path: str) -> APIConfig:
    yreader = YAMLReader()
    config = yreader.load(config=config_path)
    return config
