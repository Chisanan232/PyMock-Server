import json
from argparse import Namespace
from dataclasses import dataclass
from typing import List, Optional, Union

from ..model.enums import Format, ResponseStrategy, SampleType


@dataclass(frozen=True)
class ParserArguments:
    """*The data object for the arguments from parsing the command line of PyMock-API program*"""

    subparser_name: Optional[str]


@dataclass(frozen=True)
class _BaseSubCmdArgumentsSavingConfig(ParserArguments):
    include_template_config: bool
    base_file_path: str
    dry_run: bool
    divide_api: bool
    divide_http: bool
    divide_http_request: bool
    divide_http_response: bool


@dataclass(frozen=True)
class SubcmdRunArguments(ParserArguments):
    config: str
    app_type: str
    bind: str
    workers: int
    log_level: str


@dataclass(frozen=True)
class SubcmdAddArguments(ParserArguments):
    api_config_path: str
    api_path: str
    http_method: str
    parameters: List[dict]
    response_strategy: ResponseStrategy
    response_value: List[Union[str, dict]]

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


@dataclass(frozen=True)
class SubcmdSampleArguments(ParserArguments):
    generate_sample: bool
    print_sample: bool
    sample_output_path: str
    sample_config_type: SampleType


@dataclass(frozen=True)
class SubcmdPullArguments(_BaseSubCmdArgumentsSavingConfig):
    request_with_https: bool
    source: str
    source_file: str
    config_path: str
    base_url: str


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
        args.response_strategy = ResponseStrategy.to_enum(args.response_strategy)
        if args.parameters:
            args.parameters = list(map(lambda p: json.loads(p), args.parameters))
        if args.response_value:
            args.response_value = list(
                map(
                    lambda resp: json.loads(resp) if args.response_strategy is ResponseStrategy.OBJECT else resp,
                    args.response_value,
                )
            )
        return SubcmdAddArguments(
            subparser_name=args.subcommand,
            api_config_path=args.api_config_path,
            api_path=args.api_path,
            http_method=args.http_method,
            parameters=args.parameters,
            response_strategy=args.response_strategy,
            response_value=args.response_value,
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

    @classmethod
    def subcommand_sample(cls, args: Namespace) -> SubcmdSampleArguments:
        return SubcmdSampleArguments(
            subparser_name=args.subcommand,
            generate_sample=args.generate_sample,
            print_sample=args.print_sample,
            sample_output_path=args.file_path,
            sample_config_type=SampleType[str(args.sample_config_type).upper()],
        )

    @classmethod
    def subcommand_pull(cls, args: Namespace) -> SubcmdPullArguments:
        return SubcmdPullArguments(
            subparser_name=args.subcommand,
            request_with_https=args.request_with_https,
            source=args.source,
            source_file=args.source_file,
            config_path=args.config_path,
            base_url=args.base_url,
            include_template_config=args.include_template_config,
            base_file_path=args.base_file_path,
            dry_run=args.dry_run,
            divide_api=args.divide_api,
            divide_http=args.divide_http,
            divide_http_request=args.divide_http_request,
            divide_http_response=args.divide_http_response,
        )
