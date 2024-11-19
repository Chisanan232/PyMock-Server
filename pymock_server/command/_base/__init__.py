import glob
import pathlib
from abc import ABCMeta, abstractmethod
from typing import List

from pymock_server.command.subcommand import SubCommandLine

_Subcommand_Interface: List[SubCommandLine] = [SubCommandLine.RestServer]


class BaseAutoLoad(metaclass=ABCMeta):
    py_module: str = ""
    _current_module: str = ""

    @classmethod
    # @abstractmethod
    def import_all(cls) -> None:
        for subcmd_inf in list(map(lambda e: e.value.replace("-", "_"), _Subcommand_Interface)):
            subcmd_inf_pkg_path = cls._regex_module_paths(subcmd_inf)
            for subcmd_option_module_file_path in glob.glob(str(subcmd_inf_pkg_path), recursive=True):
                # convert the file path as Python importing
                # module path
                import_abs_path = cls._to_import_module_path(subcmd_option_module_file_path)
                # option object
                subcmd_option_obj = cls._wrap_as_object_name(cls._to_subcmd_object(subcmd_option_module_file_path))

                # import the option object by the module path
                exec(f"from {import_abs_path} import {subcmd_option_obj}")

    @classmethod
    def _regex_module_paths(cls, subcmd_inf: str) -> pathlib.Path:
        cmd_module_path = pathlib.Path(cls._current_module).parent.absolute()
        assert cls.py_module, "Python module name must not be empty."
        subcmd_inf_pkg_path = pathlib.Path(cmd_module_path, subcmd_inf, "**", cls.py_module)
        return subcmd_inf_pkg_path

    @classmethod
    def _to_import_module_path(cls, subcmd_option_module_file_path: str) -> str:
        import_style = str(subcmd_option_module_file_path).replace(".py", "").replace("/", ".")
        lib_name = "pymock_server"
        import_abs_path = ".".join([lib_name, import_style.split(f"{lib_name}.")[1]])
        return import_abs_path

    @classmethod
    @abstractmethod
    def _wrap_as_object_name(cls, subcmd_object: str) -> str:
        pass

    @classmethod
    @abstractmethod
    def _to_subcmd_object(cls, subcmd_module_file_path: str) -> str:
        pass
