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
