import glob
import os
import pathlib
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import AnyStr, Callable, List, Tuple, Union


class TestCaseDirPath(Enum):

    GET_TEST: str = "get_test"
    CHECK_TEST: str = "check_test"
    PULL_TEST: str = "pull_test"
    DIVIDE_TEST_LOAD: str = "divide_test_load"
    DIVIDE_TEST_PULL: str = "divide_test_pull"
    DESERIALIZE_OPENAPI_CONFIG_TEST: str = "deserialize_openapi_config_test"

    def generate_path_with_base_prefix_path(self, current_file: str, path: tuple) -> tuple:
        return (
            self.get_test_source_path(current_file),
            self.base_data_path,
            self.name,
            *path,
        )

    def get_test_source_path(self, current_file: str) -> str:
        tmp_dir_path = pathlib.Path(current_file).parent
        while True:
            if str(tmp_dir_path.name) == self.test_source:
                return str(tmp_dir_path)
            tmp_dir_path = tmp_dir_path.parent

    @property
    def test_source(self) -> str:
        return "test"

    @property
    def base_data_path(self) -> str:
        return "data"


class BaseTestCaseFactory(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def test_data_dir(cls) -> TestCaseDirPath:
        pass

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
        cls._ensure_path_data_type(path)
        regex_files_path = path if isinstance(path, str) else str(os.path.join(*path))
        for json_config_path in glob.glob(regex_files_path):
            generate_test_case_callback(json_config_path)

    @classmethod
    def _iterate_files_by_paths(
        cls, paths: Tuple, generate_test_case_callback: Callable[[tuple], None], sort: bool = False
    ) -> None:

        def _glob_files(path: Union[str, tuple]) -> List[str]:
            glob_files = glob.glob(path if isinstance(path, str) else os.path.join(*path))
            if sort:
                return sorted(glob_files)
            return glob_files

        glob_files_from_dirs = (_glob_files(path) for path in paths)
        for pair_paths in zip(*glob_files_from_dirs):
            generate_test_case_callback(pair_paths)

    @classmethod
    def _iterate_files_by_directory(
        cls,
        path: Union[AnyStr, Tuple],
        generate_dir_paths: Callable[[str], tuple],
        generate_test_case_callback: Callable[[tuple], None],
    ) -> None:
        cls._ensure_path_data_type(path)
        regex_files_path = path if isinstance(path, str) else str(os.path.join(*path))
        for folder_path in os.listdir(regex_files_path):
            dir_paths: tuple = generate_dir_paths(folder_path)
            cls._iterate_files_by_paths(
                paths=dir_paths,
                generate_test_case_callback=generate_test_case_callback,
            )

    @classmethod
    def _ensure_path_data_type(cls, path: Union[AnyStr, Tuple]) -> None:
        if not isinstance(path, (str, tuple)):
            raise TypeError("The parameter *path* only accept 'str' or 'Tuple[str]' types.")
