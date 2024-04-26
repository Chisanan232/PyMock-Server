import glob
import os
from abc import ABCMeta, abstractmethod
from typing import Callable, List, Tuple, Union


class BaseTestCaseFactory(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def get_test_case(cls) -> Union[List, Tuple]:
        pass

    @classmethod
    @abstractmethod
    def load(cls, *args, **kwargs) -> None:
        pass

    @classmethod
    def _iterate_files_by_path(cls, path: Tuple, generate_test_case_callback: Callable[[str], None]) -> None:
        json_dir = os.path.join(*path)
        for json_config_path in glob.glob(json_dir):
            generate_test_case_callback(json_config_path)
