import argparse
import re
from dataclasses import dataclass
from typing import List, Optional

from fake_api_server.command.subcommand import SubCommandLine, SubCommandSection


@dataclass
class SysArg:
    subcmd: SubCommandLine
    pre_subcmd: Optional["SysArg"] = None

    @staticmethod
    def parse(args: List[str]) -> "SysArg":
        if not args:
            return SysArg(subcmd=SubCommandLine.Base)

        no_pyfile_subcmds = list(filter(lambda a: not re.search(r".{1,1024}.py", a), args))
        subcmds: List[str] = []
        for subcmd_or_options in no_pyfile_subcmds:
            search_subcmd = re.search(r"-.{1,256}", subcmd_or_options)
            if search_subcmd and len(search_subcmd.group(0)) == len(subcmd_or_options):
                break
            subcmds.append(subcmd_or_options)

        if len(subcmds) == 0:
            return SysArg(subcmd=SubCommandLine.Base)
        elif len(subcmds) == 1:
            return SysArg(
                pre_subcmd=SysArg(
                    pre_subcmd=None,
                    subcmd=SubCommandLine.Base,
                ),
                subcmd=SubCommandLine.to_enum(subcmds[0]),
            )
        else:
            return SysArg(
                pre_subcmd=SysArg.parse(subcmds[:-1]),
                subcmd=SubCommandLine.to_enum(subcmds[-1]),
            )


@dataclass
class SubCmdParserAction:
    subcmd_name: SubCommandLine
    subcmd_parser: argparse._SubParsersAction


@dataclass
class SubCmdParser:
    in_subcmd: SubCommandLine
    parser: argparse.ArgumentParser
    sub_parser: List["SubCmdParser"]

    def find(self, subcmd: SubCommandLine) -> Optional[argparse.ArgumentParser]:
        if subcmd is self.in_subcmd:
            return self.parser
        else:
            if self.sub_parser:
                all_subcmd_parser = list(map(lambda sp: sp.find(subcmd), self.sub_parser))
                exist_subcmd_parser = list(filter(lambda sp: sp is not None, all_subcmd_parser))
                if exist_subcmd_parser:
                    return exist_subcmd_parser[0]
                return None
            else:
                return None


@dataclass
class SubCommandAttr:
    title: SubCommandSection
    dest: SubCommandLine
    description: str
    help: str


@dataclass
class SubParserAttr:
    name: SubCommandLine
    help: str
