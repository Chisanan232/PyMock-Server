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


class CannotParsingAPIDocumentVersion(ValueError):
    def __str__(self):
        return "Cannot parsing the configuration to get the specific property to identify which version it is."


class NotSupportAPIDocumentVersion(ValueError):
    def __init__(self, version: str):
        self._version = version

    def __str__(self):
        return f"Currently, it doesn't support processing the configuration of API document version {self._version}."


class NotFoundCommandLine(ValueError):
    def __init__(self, subcmd: str):
        self.subcmd = subcmd

    def __str__(self):
        return f"Cannot map anyone subcommand line with value '{self.subcmd}'."
