import glob
import pathlib
from abc import ABCMeta, abstractmethod
from typing import List

from fake_api_server.command.subcommand import SubCommandLine

_Major_Subcommand_Interface: List[SubCommandLine] = SubCommandLine.major_cli()


class BaseAutoLoad(metaclass=ABCMeta):
    @property
    def py_module(self) -> str:
        return pathlib.Path(self._current_module).name

    @property
    @abstractmethod
    def _current_module(self) -> str:
        pass

    def import_all(self) -> None:
        for subcmd_inf in list(map(lambda e: e.value.replace("-", "_"), _Major_Subcommand_Interface)):
            subcmd_inf_pkg_path = self._regex_module_paths(subcmd_inf)
            for subcmd_prop_module_file_path in glob.glob(str(subcmd_inf_pkg_path), recursive=True):
                # convert the file path as Python importing
                # module path
                import_abs_path = self._to_import_module_path(subcmd_prop_module_file_path)
                # option object
                subcmd_option_obj = self._wrap_as_object_name(self._to_subcmd_object(subcmd_prop_module_file_path))

                # import the option object by the module path
                exec(f"from {import_abs_path} import {subcmd_option_obj}")

    def _regex_module_paths(self, subcmd_inf: str) -> pathlib.Path:
        cmd_module_path = pathlib.Path(self._current_module).parent.absolute()
        subcmd_inf_pkg_path = pathlib.Path(cmd_module_path, subcmd_inf, "**", self.py_module)
        return subcmd_inf_pkg_path

    def _to_import_module_path(self, subcmd_prop_module_file_path: str) -> str:
        import_style = str(subcmd_prop_module_file_path).replace(".py", "").replace("/", ".")
        lib_name = "fake_api_server"
        import_abs_path = ".".join([lib_name, import_style.split(f"{lib_name}.")[1]])
        return import_abs_path

    @abstractmethod
    def _wrap_as_object_name(self, subcmd_object: str) -> str:
        pass

    def _to_subcmd_object(self, subcmd_prop_module_file_path: str) -> str:
        subcmd_dir = pathlib.Path(subcmd_prop_module_file_path).parent.name
        subcmd_sub_pkg_name_parts = subcmd_dir.split("_")
        subcmd_option_obj: str = ""
        for part in subcmd_sub_pkg_name_parts:
            subcmd_option_obj += part[0].upper() + part[1:]
        return subcmd_option_obj
