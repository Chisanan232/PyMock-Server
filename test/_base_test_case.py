import glob
import os
from abc import ABCMeta, abstractmethod
from typing import AnyStr, Callable, List, Tuple, Union


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
    def _iterate_files_by_path(
        cls, path: Union[AnyStr, Tuple], generate_test_case_callback: Callable[[str], None]
    ) -> None:
        if not isinstance(path, (str, tuple)):
            raise TypeError("The parameter *path* only accept 'str' or 'Tuple[str]' types.")
        regex_files_path = path if isinstance(path, str) else str(os.path.join(*path))
        for json_config_path in glob.glob(regex_files_path):
            generate_test_case_callback(json_config_path)

    @classmethod
    def _iterate_files_by_paths(cls, paths: Tuple, generate_test_case_callback: Callable[[tuple], None]) -> None:
        glob_files_from_dirs = (glob.glob(os.path.join(*path)) for path in paths)
        for pair_paths in zip(*glob_files_from_dirs):
            generate_test_case_callback(pair_paths)

    @classmethod
    def _iterate_files_by_directory(
        cls, path: Union[AnyStr, Tuple], generate_test_case_from_folder_callback: Callable[[str], None]
    ) -> None:
        if not isinstance(path, (str, tuple)):
            raise TypeError("The parameter *path* only accept 'str' or 'Tuple[str]' types.")
        regex_files_path = path if isinstance(path, str) else str(os.path.join(*path))
        for folder_path in os.listdir(regex_files_path):
            generate_test_case_from_folder_callback(folder_path)
