import re
from collections import namedtuple
from typing import List, Tuple

from ._global_value import SubCommandInterface

COMMAND_OPTIONS: List["MetaCommandOption"] = []


class CommandLineOptions:
    @staticmethod
    def get() -> List["MetaCommandOption"]:
        return COMMAND_OPTIONS

    @staticmethod
    def append(v: "MetaCommandOption") -> None:
        assert isinstance(v, MetaCommandOption)
        global COMMAND_OPTIONS
        COMMAND_OPTIONS.append(v)

    @staticmethod
    def pop(index: int) -> None:
        global COMMAND_OPTIONS
        COMMAND_OPTIONS.pop(index)


_ClsNamingFormat = namedtuple("_ClsNamingFormat", ["ahead", "tail"])
_ClsNamingFormat.ahead = "BaseSubCmd"
_ClsNamingFormat.tail = "Option"


class MetaCommandOption(type):
    """*The metaclass for options of PyMock-API command*

    content ...
    """

    def __new__(cls, name: str, bases: Tuple[type], attrs: dict):
        super_new = super().__new__
        parent = [b for b in bases if isinstance(b, MetaCommandOption)]
        if not parent:
            return super_new(cls, name, bases, attrs)
        parent_is_subcmd = list(
            filter(
                lambda b: re.search(
                    re.escape(_ClsNamingFormat.ahead) + r"\w{1,10}" + re.escape(_ClsNamingFormat.tail), b.__name__
                ),
                bases,
            )
        )
        if parent_is_subcmd:
            SubCommandInterface.extend(
                [
                    b.__name__.replace(_ClsNamingFormat.ahead, "").replace(_ClsNamingFormat.tail, "").lower()
                    for b in bases
                ]
            )
        new_class = super_new(cls, name, bases, attrs)
        CommandLineOptions.append(new_class)
        return new_class
