import json
from argparse import Namespace
from dataclasses import dataclass
from typing import List, Optional

from ..model.enums import Format


@dataclass(frozen=True)
class ParserArguments:
    """*The data object for the arguments from parsing the command line of PyMock-API program*"""

    subparser_name: Optional[str]


@dataclass(frozen=True)
class SubcmdRunArguments(ParserArguments):
    config: str
    app_type: str
    bind: str
    workers: int
    log_level: str


@dataclass(frozen=True)
class SubcmdAddArguments(ParserArguments):
    generate_sample: bool
    print_sample: bool
    sample_output_path: str
    api_config_path: str
    api_path: str
    http_method: str
    parameters: List[dict]
    response: str

    def api_info_is_complete(self) -> bool:
        def _string_is_not_empty(s: Optional[str]) -> bool:
            if s is not None:
                s = s.replace(" ", "")
                return s != ""
            return False

        string_chksum = list(map(_string_is_not_empty, [self.api_config_path, self.api_path]))
        return False not in string_chksum


@dataclass(frozen=True)
class SubcmdCheckArguments(ParserArguments):
    config_path: str
    swagger_doc_url: str
    stop_if_fail: bool
    check_api_path: bool
    check_api_http_method: bool
    check_api_parameters: bool


@dataclass(frozen=True)
class SubcmdGetArguments(ParserArguments):
    config_path: str
    show_detail: bool
    show_as_format: Format
    api_path: str
    http_method: str


class DeserializeParsedArgs:
    """*Deserialize the object *argparse.Namespace* to *ParserArguments*"""

    @classmethod
    def subcommand_run(cls, args: Namespace) -> SubcmdRunArguments:
        return SubcmdRunArguments(
            subparser_name=args.subcommand,
            config=args.config,
            app_type=args.app_type,
            bind=args.bind,
            workers=args.workers,
            log_level=args.log_level,
        )

    @classmethod
    def subcommand_add(cls, args: Namespace) -> SubcmdAddArguments:
        if args.parameters:
            args.parameters = list(map(lambda p: json.loads(p), args.parameters))
        return SubcmdAddArguments(
            subparser_name=args.subcommand,
            generate_sample=args.generate_sample,
            print_sample=args.print_sample,
            sample_output_path=args.file_path,
            api_config_path=args.api_config_path,
            api_path=args.api_path,
            http_method=args.http_method,
            parameters=args.parameters,
            response=args.response,
        )

    @classmethod
    def subcommand_check(cls, args: Namespace) -> SubcmdCheckArguments:
        if hasattr(args, "check_entire_api") and args.check_entire_api:
            args.check_api_path = True
            args.check_api_http_method = True
            args.check_api_parameters = True
        return SubcmdCheckArguments(
            subparser_name=args.subcommand,
            config_path=args.config_path,
            swagger_doc_url=args.swagger_doc_url,
            stop_if_fail=args.stop_if_fail,
            check_api_path=args.check_api_path,
            check_api_http_method=args.check_api_http_method,
            check_api_parameters=args.check_api_parameters,
        )

    @classmethod
    def subcommand_get(cls, args: Namespace) -> SubcmdGetArguments:
        return SubcmdGetArguments(
            subparser_name=args.subcommand,
            config_path=args.config_path,
            show_detail=args.show_detail,
            show_as_format=Format[str(args.show_as_format).upper()],
            api_path=args.api_path,
            http_method=args.http_method,
        )
