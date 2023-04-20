from typing import Callable, List, Union


class FileFormatNotSupport(RuntimeError):
    def __init__(self, valid_file_format: List[str]):
        self._valid_file_format = valid_file_format

    def __str__(self):
        return f"It doesn't support reading '{', '.join(self._valid_file_format)}' format file."


class FunctionNotFoundError(RuntimeError):
    def __init__(self, function: Union[str, Callable]):
        self._function = str(function.__qualname__ if isinstance(function, Callable) else function)  # type: ignore

    def __str__(self):
        return f"Cannot find the function {self._function} in current module."


class NoValidWebLibrary(RuntimeError):
    def __str__(self):
        return (
            "Cannot initial and set up server gateway because current runtime environment doesn't have valid web "
            "library."
        )


class InvalidAppType(ValueError):
    def __str__(self):
        return "Invalid value at argument *app-type*. It only supports 'auto', 'flask' or 'fastapi' currently."


class OptionValueCannotBeEmpty(ValueError):
    def __init__(self, cmd_option: str):
        self._cmd_option = cmd_option

    def __str__(self):
        return f"Option '{self._cmd_option}' value cannot be empty."


class BrokenConfigError(RuntimeError):
    def __init__(self, config_prop: Union[str, List[str]]):
        self._config_prop = (
            ", ".join([f"*{cp}*" for cp in config_prop]) if isinstance(config_prop, list) else config_prop
        )

    def __str__(self):
        return f"Config value of properties {self._config_prop} should not be empty here."
